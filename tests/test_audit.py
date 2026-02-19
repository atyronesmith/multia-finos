"""Tests for Phase 13, 15: Audit trail, compliance report, scoring function IDs."""

import json

import pytest

from src.governance.audit import AuditTrail
from src.governance.compliance_report import generate_compliance_report, FINOS_MITIGATIONS
from src.evaluation.scoring_setup import get_scoring_function_ids


# ── AuditTrail ───────────────────────────────────────────────────────────

class TestAuditTrail:
    def test_record_shield(self, sample_audit):
        shield_entries = [e for e in sample_audit.entries if e.category == "shield"]
        assert len(shield_entries) >= 1
        assert shield_entries[0].layer == "7-Security"

    def test_record_policy(self, sample_audit):
        policy_entries = [e for e in sample_audit.entries if e.category == "policy"]
        assert len(policy_entries) >= 1
        assert policy_entries[0].layer == "2-Orchestration"

    def test_record_evaluation(self, sample_audit):
        eval_entries = [e for e in sample_audit.entries if e.category == "evaluation"]
        assert len(eval_entries) >= 1
        assert "score=7.5" in eval_entries[0].detail

    def test_to_dict_summary(self, sample_audit):
        d = sample_audit.to_dict()
        assert d["summary"]["total_entries"] == len(sample_audit.entries)
        assert d["summary"]["passes"] > 0
        assert "layers_covered" in d["summary"]

    def test_save_json(self, sample_audit, tmp_path):
        path = tmp_path / "audit.json"
        sample_audit.save_json(path)
        data = json.loads(path.read_text())
        assert data["evaluation_id"] == "test-001"

    def test_save_markdown(self, sample_audit, tmp_path):
        path = tmp_path / "audit.md"
        sample_audit.save_markdown(path)
        md = path.read_text()
        assert "# Audit Trail:" in md
        assert "| Time |" in md


# ── ComplianceReport ─────────────────────────────────────────────────────

class TestComplianceReport:
    def test_full_coverage_positive(self, sample_audit):
        report = generate_compliance_report(sample_audit)
        assert report.coverage_pct > 0

    def test_empty_audit_zero_coverage(self):
        empty = AuditTrail(evaluation_id="empty")
        report = generate_compliance_report(empty)
        assert report.coverage_pct == 0

    def test_mitigation_count(self, sample_audit):
        report = generate_compliance_report(sample_audit)
        assert len(report.mitigations) == 17

    def test_markdown_output(self, sample_audit):
        report = generate_compliance_report(sample_audit)
        md = report.to_markdown()
        assert "FINOS Compliance Report" in md
        assert "MI-1" in md

    def test_specific_mitigations_covered(self, sample_audit):
        report = generate_compliance_report(sample_audit)
        covered_ids = {m.mitigation_id for m in report.mitigations if m.covered}
        # The sample_audit has entries covering these layers/categories
        assert "MI-14" in covered_ids  # encryption entry
        assert "MI-17" in covered_ids  # policy entry


# ── Scoring Function IDs ────────────────────────────────────────────────

class TestScoringFunctionIDs:
    def test_loads_from_yaml(self):
        ids = get_scoring_function_ids()
        assert len(ids) == 4

    def test_ids_have_prefix(self):
        ids = get_scoring_function_ids()
        assert all(fn_id.startswith("multia-") for fn_id in ids)

    def test_expected_dimensions(self):
        ids = get_scoring_function_ids()
        names = {fn_id.removeprefix("multia-") for fn_id in ids}
        assert names == {"quality", "consistency", "completeness", "bias"}
