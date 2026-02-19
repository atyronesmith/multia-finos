"""Tests for Phase 12: Alerts, bias detector."""

import pytest

from src.observability.alerts import AlertCollector
from src.evaluation.bias_detector import detect_bias


# ── AlertCollector ───────────────────────────────────────────────────────

class TestAlertCollector:
    def test_no_issues(self):
        ac = AlertCollector()
        ac.record_shield_result("market", passed=True)
        ac.record_policy_decision("market", allowed=True)
        ac.record_score("market", 7.0)
        alerts = ac.evaluate()
        assert len(alerts) == 0

    def test_below_threshold_no_alert(self):
        ac = AlertCollector()
        ac.record_shield_result("market", passed=False)  # 1 violation, threshold is 2
        alerts = ac.evaluate()
        assert not any(a.rule == "shield_violations" for a in alerts)

    def test_shield_violations_trigger(self):
        ac = AlertCollector()
        ac.record_shield_result("a", passed=False)
        ac.record_shield_result("b", passed=False)
        alerts = ac.evaluate()
        shield_alerts = [a for a in alerts if a.rule == "shield_violations"]
        assert len(shield_alerts) == 1
        assert shield_alerts[0].severity == "critical"

    def test_policy_denials_trigger(self):
        ac = AlertCollector()
        for _ in range(3):
            ac.record_policy_decision("x", allowed=False)
        alerts = ac.evaluate()
        policy_alerts = [a for a in alerts if a.rule == "policy_denials"]
        assert len(policy_alerts) == 1
        assert policy_alerts[0].severity == "warn"

    def test_low_scores(self):
        ac = AlertCollector()
        ac.record_score("market", 2.0)
        ac.record_score("tech", 1.5)
        alerts = ac.evaluate()
        score_alerts = [a for a in alerts if a.rule == "low_scores"]
        assert len(score_alerts) == 1
        assert "market" in score_alerts[0].message

    def test_multiple_rules(self):
        ac = AlertCollector()
        ac.record_shield_result("a", passed=False)
        ac.record_shield_result("b", passed=False)
        ac.record_score("c", 1.0)
        alerts = ac.evaluate()
        rules = {a.rule for a in alerts}
        assert "shield_violations" in rules
        assert "low_scores" in rules

    def test_custom_thresholds(self):
        ac = AlertCollector(shield_violation_threshold=1)
        ac.record_shield_result("a", passed=False)
        alerts = ac.evaluate()
        assert any(a.rule == "shield_violations" for a in alerts)


# ── BiasDetector ─────────────────────────────────────────────────────────

class TestBiasDetector:
    def test_insufficient_data(self):
        report = detect_bias([{"idea": "x", "scores": {"a": 5}, "recommendation": "GO"}])
        assert report.bias_detected is False
        assert any(c["name"] == "sample_size" for c in report.checks)

    def test_narrow_score_range(self):
        history = [
            {"idea": "a", "scores": {"market": 7.0, "tech": 7.2}, "recommendation": "GO"},
            {"idea": "b", "scores": {"market": 7.1, "tech": 7.3}, "recommendation": "GO"},
        ]
        report = detect_bias(history)
        range_check = next(c for c in report.checks if c["name"] == "score_range")
        assert range_check["passed"] is False  # range < 1.5

    def test_healthy_variance(self):
        history = [
            {"idea": "a", "scores": {"market": 3.0, "tech": 8.0}, "recommendation": "NO-GO"},
            {"idea": "b", "scores": {"market": 7.0, "tech": 5.0}, "recommendation": "GO"},
        ]
        report = detect_bias(history)
        range_check = next(c for c in report.checks if c["name"] == "score_range")
        assert range_check["passed"] is True

    def test_recommendation_skew(self):
        history = [
            {"idea": f"idea{i}", "scores": {"a": 8}, "recommendation": "GO"}
            for i in range(4)
        ]
        report = detect_bias(history)
        skew_check = next(c for c in report.checks if c["name"] == "recommendation_skew")
        assert skew_check["passed"] is False

    def test_agent_low_variance(self):
        history = [
            {"idea": f"idea{i}", "scores": {"market": 7.0}, "recommendation": "GO"}
            for i in range(4)
        ]
        report = detect_bias(history)
        variance_checks = [c for c in report.checks if c["name"].startswith("agent_")]
        assert any(not c["passed"] for c in variance_checks)
