"""Audit trail collector for pipeline runs.

Collects decision points from a pipeline run into a structured audit
trail. Can query LlamaStack telemetry when a server is available,
or collect events directly during a run.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from llama_stack_client import LlamaStackClient

logger = logging.getLogger(__name__)

AUDIT_DIR = Path(__file__).resolve().parent.parent.parent / ".audit"


@dataclass
class AuditEntry:
    timestamp: str
    layer: str  # FINOS layer name
    category: str  # e.g. "shield", "policy", "evaluation"
    action: str
    detail: str
    outcome: str  # "pass", "fail", "info"


@dataclass
class AuditTrail:
    """Collects audit entries for a single pipeline run."""

    evaluation_id: str
    startup_idea: str = ""
    started_at: str = ""
    entries: list[AuditEntry] = field(default_factory=list)

    def record(self, layer: str, category: str, action: str, detail: str, outcome: str = "info"):
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            layer=layer,
            category=category,
            action=action,
            detail=detail,
            outcome=outcome,
        )
        self.entries.append(entry)
        return entry

    def record_input_validation(self, passed: bool, detail: str = ""):
        self.record("1-Input", "validation", "input_check", detail, "pass" if passed else "fail")

    def record_shield(self, shield_id: str, agent_name: str, passed: bool, message: str = ""):
        self.record(
            "7-Security", "shield", f"shield:{shield_id}",
            f"agent={agent_name} message={message}",
            "pass" if passed else "fail",
        )

    def record_policy(self, agent_name: str, resource: str, allowed: bool, reason: str = ""):
        self.record(
            "2-Orchestration", "policy", f"policy_check:{resource}",
            f"agent={agent_name} reason={reason}",
            "pass" if allowed else "fail",
        )

    def record_tool_governance(self, tool_name: str, tier: str, allowed: bool):
        self.record(
            "4-Tools", "governance", f"tool_check:{tool_name}",
            f"tier={tier}",
            "pass" if allowed else "fail",
        )

    def record_evaluation(self, agent_name: str, score: float):
        self.record(
            "3-Agent", "evaluation", f"agent_score:{agent_name}",
            f"score={score}/10",
            "info",
        )

    def record_sanitization(self, redaction_count: int, types: list[str]):
        self.record(
            "5-Model", "sanitization", "pii_redaction",
            f"redacted={redaction_count} types={types}",
            "pass" if redaction_count == 0 else "info",
        )

    def record_mcp_registration(self, server_name: str, endpoint: str, success: bool):
        self.record(
            "4-Tools", "mcp", f"mcp_register:{server_name}",
            f"endpoint={endpoint}",
            "pass" if success else "fail",
        )

    def record_mcp_access(self, server_name: str, tool_name: str, allowed: bool, reason: str = ""):
        self.record(
            "4-Tools", "mcp_governance", f"mcp_access:{server_name}/{tool_name}",
            f"reason={reason}",
            "pass" if allowed else "fail",
        )

    def record_output_filter(self, passed: bool, detections: int = 0):
        self.record(
            "9-Output", "filter", "secret_scan",
            f"detections={detections}",
            "pass" if passed else "fail",
        )

    def record_scoring(self, dimension: str, score: float):
        self.record(
            "9-Output", "scoring", f"llm_judge:{dimension}",
            f"score={score}",
            "info",
        )

    def record_encryption(self, evaluation_id: str, action: str):
        self.record(
            "3-Agent", "encryption", f"state_{action}",
            f"evaluation_id={evaluation_id}",
            "info",
        )

    def to_dict(self) -> dict:
        return {
            "evaluation_id": self.evaluation_id,
            "startup_idea": self.startup_idea,
            "started_at": self.started_at,
            "entries": [asdict(e) for e in self.entries],
            "summary": {
                "total_entries": len(self.entries),
                "passes": sum(1 for e in self.entries if e.outcome == "pass"),
                "failures": sum(1 for e in self.entries if e.outcome == "fail"),
                "layers_covered": sorted(set(e.layer for e in self.entries)),
            },
        }

    def save_json(self, path: Path | None = None):
        """Save audit trail as JSON."""
        AUDIT_DIR.mkdir(exist_ok=True)
        if path is None:
            path = AUDIT_DIR / f"{self.evaluation_id}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2))
        logger.info("Saved audit trail: %s", path)

    def save_markdown(self, path: Path | None = None):
        """Save audit trail as human-readable markdown."""
        AUDIT_DIR.mkdir(exist_ok=True)
        if path is None:
            path = AUDIT_DIR / f"{self.evaluation_id}.md"

        data = self.to_dict()
        lines = [
            f"# Audit Trail: {self.evaluation_id}",
            "",
            f"**Startup Idea:** {self.startup_idea}",
            f"**Started:** {self.started_at}",
            f"**Total Entries:** {data['summary']['total_entries']}",
            f"**Passes:** {data['summary']['passes']}",
            f"**Failures:** {data['summary']['failures']}",
            f"**Layers Covered:** {', '.join(data['summary']['layers_covered'])}",
            "",
            "## Entries",
            "",
            "| Time | Layer | Category | Action | Detail | Outcome |",
            "|------|-------|----------|--------|--------|---------|",
        ]
        for e in self.entries:
            ts = e.timestamp.split("T")[1][:8] if "T" in e.timestamp else e.timestamp
            lines.append(f"| {ts} | {e.layer} | {e.category} | {e.action} | {e.detail} | {e.outcome} |")

        path.write_text("\n".join(lines) + "\n")
        logger.info("Saved audit trail markdown: %s", path)


def collect_from_telemetry(
    client: LlamaStackClient,
    trace_id: str,
    root_span_id: str,
) -> list[dict]:
    """Query LlamaStack telemetry for spans from a pipeline trace."""
    try:
        tree = client.telemetry.get_span_tree(root_span_id, max_depth=10)
        if isinstance(tree, dict):
            return [{"span_id": k, **v} for k, v in tree.items() if isinstance(v, dict)]
        return []
    except Exception as e:
        logger.warning("Could not query telemetry: %s", e)
        return []
