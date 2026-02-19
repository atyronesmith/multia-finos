"""Tests for Phase 11: Calculator, market_data, complexity, risk_checklist."""

import json

import pytest

from src.tools.calculator import calculator
from src.tools.market_data import search_comparables
from src.tools.complexity import complexity_estimator
from src.tools.risk_checklist import risk_checklist


# ── Calculator ───────────────────────────────────────────────────────────

class TestCalculator:
    def test_add(self):
        assert calculator("add", 2, 3) == 5.0

    def test_subtract(self):
        assert calculator("subtract", 10, 4) == 6.0

    def test_multiply(self):
        assert calculator("multiply", 3, 7) == 21.0

    def test_divide(self):
        assert calculator("divide", 10, 4) == 2.5

    def test_divide_by_zero(self):
        result = calculator("divide", 10, 0)
        assert result == float("inf")

    def test_percentage(self):
        assert calculator("percentage", 25, 200) == pytest.approx(12.5)

    def test_unknown_operation(self):
        result = calculator("modulo", 5, 3)
        assert isinstance(result, str)
        assert "Unknown operation" in result


# ── Market Data ──────────────────────────────────────────────────────────

class TestMarketData:
    def test_fintech_results(self):
        result = json.loads(search_comparables("fintech"))
        assert "results" in result
        assert len(result["results"]) > 0

    def test_no_match_fallback(self):
        result = json.loads(search_comparables("quantum_teleportation_xyz"))
        assert "note" in result
        assert len(result["results"]) > 0  # returns sample comparables


# ── Complexity ───────────────────────────────────────────────────────────

class TestComplexity:
    def test_low_complexity(self):
        result = complexity_estimator("web app, database", "no", "no")
        assert "3/10" in result
        assert "2-3 engineers" in result

    def test_high_with_hardware(self):
        result = complexity_estimator(
            "computer vision, IoT sensors, ML pipeline, web dashboard, mobile app",
            "yes", "yes",
        )
        score_line = result.split("\n")[0]
        assert "/10" in score_line
        assert "15+" in result or "8-15" in result

    def test_team_size_scales(self):
        low = complexity_estimator("api", "no", "no")
        high = complexity_estimator("a, b, c, d, e, f, g, h", "yes", "yes")
        assert "2-3" in low
        assert "15+" in high


# ── Risk Checklist ───────────────────────────────────────────────────────

class TestRiskChecklist:
    def test_valid_category(self):
        result = risk_checklist("market")
        assert "Risk Checklist: MARKET" in result
        assert "Impact:" in result

    def test_all_categories(self):
        for cat in ["market", "technology", "financial", "regulatory", "team", "operational"]:
            result = risk_checklist(cat)
            assert "Risk Checklist:" in result

    def test_unknown_category(self):
        result = risk_checklist("alien_invasion")
        assert "Unknown category" in result
        assert "Available categories" in result
