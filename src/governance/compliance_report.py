"""FINOS mitigation coverage report generator."""

from dataclasses import dataclass, field

from src.governance.audit import AuditTrail

# FINOS mitigations and which layers/categories demonstrate them
FINOS_MITIGATIONS = {
    "MI-1": {
        "name": "Data Leakage Prevention",
        "phase": 10,
        "layers": ["5-Model", "7-Security"],
        "categories": ["sanitization", "shield"],
    },
    "MI-3": {
        "name": "Firewalling",
        "phase": "7, 9",
        "layers": ["1-Input", "7-Security"],
        "categories": ["validation", "shield"],
    },
    "MI-4": {
        "name": "AI System Observability",
        "phase": 12,
        "layers": ["*"],
        "categories": ["*"],
    },
    "MI-5": {
        "name": "Acceptance Testing",
        "phase": 13,
        "layers": ["9-Output"],
        "categories": ["scoring"],
    },
    "MI-6": {
        "name": "Data Classification",
        "phase": 10,
        "layers": ["5-Model"],
        "categories": ["sanitization"],
    },
    "MI-7": {
        "name": "Legal Frameworks",
        "phase": 15,
        "layers": ["*"],
        "categories": ["*"],
    },
    "MI-8": {
        "name": "QoS/DDoS",
        "phase": 7,
        "layers": ["1-Input"],
        "categories": ["validation"],
    },
    "MI-9": {
        "name": "Alerting",
        "phase": 12,
        "layers": ["*"],
        "categories": ["*"],
    },
    "MI-13": {
        "name": "Citations",
        "phase": 15,
        "layers": ["*"],
        "categories": ["*"],
    },
    "MI-14": {
        "name": "Encryption at Rest",
        "phase": 14,
        "layers": ["3-Agent"],
        "categories": ["encryption"],
    },
    "MI-15": {
        "name": "LLM-as-Judge",
        "phase": 13,
        "layers": ["9-Output"],
        "categories": ["scoring"],
    },
    "MI-17": {
        "name": "AI Firewall",
        "phase": 8,
        "layers": ["2-Orchestration"],
        "categories": ["policy"],
    },
    "MI-18": {
        "name": "Agent Least Privilege",
        "phase": 8,
        "layers": ["2-Orchestration"],
        "categories": ["policy"],
    },
    "MI-19": {
        "name": "Tool Chain Validation",
        "phase": 11,
        "layers": ["4-Tools"],
        "categories": ["governance"],
    },
    "MI-20": {
        "name": "MCP Security Governance",
        "phase": 11,
        "layers": ["4-Tools"],
        "categories": ["governance"],
    },
    "MI-21": {
        "name": "Explainability",
        "phase": "13, 15",
        "layers": ["9-Output"],
        "categories": ["scoring"],
    },
    "MI-22": {
        "name": "Agent Isolation",
        "phase": "9, 14",
        "layers": ["3-Agent", "7-Security"],
        "categories": ["shield", "encryption"],
    },
}


@dataclass
class MitigationStatus:
    mitigation_id: str
    name: str
    phase: str | int
    covered: bool
    evidence_count: int
    detail: str


@dataclass
class ComplianceReport:
    evaluation_id: str
    mitigations: list[MitigationStatus] = field(default_factory=list)
    coverage_pct: float = 0.0

    def to_markdown(self) -> str:
        lines = [
            f"# FINOS Compliance Report: {self.evaluation_id}",
            "",
            f"**Coverage:** {self.coverage_pct:.0f}% ({sum(1 for m in self.mitigations if m.covered)}/{len(self.mitigations)} mitigations)",
            "",
            "| Mitigation | Name | Phase | Covered | Evidence | Detail |",
            "|------------|------|-------|---------|----------|--------|",
        ]
        for m in self.mitigations:
            covered = "Yes" if m.covered else "No"
            lines.append(f"| {m.mitigation_id} | {m.name} | {m.phase} | {covered} | {m.evidence_count} | {m.detail} |")
        return "\n".join(lines) + "\n"


def generate_compliance_report(audit: AuditTrail) -> ComplianceReport:
    """Generate a FINOS mitigation coverage report from an audit trail."""
    report = ComplianceReport(evaluation_id=audit.evaluation_id)

    for mit_id, mit_info in FINOS_MITIGATIONS.items():
        # Count matching audit entries
        evidence = []
        for entry in audit.entries:
            layer_match = "*" in mit_info["layers"] or entry.layer in mit_info["layers"]
            cat_match = "*" in mit_info["categories"] or entry.category in mit_info["categories"]
            if layer_match and cat_match:
                evidence.append(entry)

        covered = len(evidence) > 0
        detail = f"{len(evidence)} audit entries" if evidence else "no evidence in this run"

        report.mitigations.append(MitigationStatus(
            mitigation_id=mit_id,
            name=mit_info["name"],
            phase=mit_info["phase"],
            covered=covered,
            evidence_count=len(evidence),
            detail=detail,
        ))

    total = len(report.mitigations)
    covered = sum(1 for m in report.mitigations if m.covered)
    report.coverage_pct = (covered / total * 100) if total else 0

    return report
