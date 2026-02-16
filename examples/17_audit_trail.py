"""Phase 15: Demonstrate audit trail and FINOS compliance report.

Simulates a full pipeline run with audit events across all 9 FINOS layers,
then generates a compliance coverage report.
"""

from src.governance.audit import AuditTrail
from src.governance.compliance_report import generate_compliance_report


def main():
    # Create audit trail for a simulated pipeline run
    audit = AuditTrail(evaluation_id="audit-demo-001", startup_idea="AI indoor farming platform")
    audit.started_at = "2026-02-16T10:00:00Z"

    # Layer 1: Input
    audit.record_input_validation(passed=True, detail="Request validated, rate limit ok")

    # Layer 2: Orchestration (policy engine)
    audit.record_policy("market", "search_comparables", allowed=True, reason="ok")
    audit.record_policy("market", "calculator", allowed=False, reason="Not in allowed tools")

    # Layer 3: Agent evaluations
    audit.record_evaluation("market", 7.0)
    audit.record_evaluation("tech", 6.5)
    audit.record_evaluation("finance", 7.0)
    audit.record_evaluation("risk", 6.0)

    # Layer 4: Tool governance
    audit.record_tool_governance("search_comparables", tier="approved", allowed=True)
    audit.record_tool_governance("calculator", tier="approved", allowed=True)
    audit.record_tool_governance("shell_exec", tier="blocked", allowed=False)

    # Layer 5: Sanitization
    audit.record_sanitization(redaction_count=2, types=["email", "phone_us"])

    # Layer 7: Shield checks
    audit.record_shield("prompt-guard", "user-input", passed=True)
    audit.record_shield("prompt-guard", "market", passed=True)
    audit.record_shield("prompt-guard", "tech", passed=True)
    audit.record_shield("prompt-guard", "finance", passed=True)
    audit.record_shield("prompt-guard", "risk", passed=True)

    # Layer 3: Encryption
    audit.record_encryption("audit-demo-001", "save")

    # Layer 9: Output scoring
    audit.record_scoring("quality", 4.0)
    audit.record_scoring("consistency", 5.0)
    audit.record_scoring("completeness", 4.0)
    audit.record_scoring("bias", 5.0)

    # Layer 9: Output filter
    audit.record_output_filter(passed=True, detections=0)

    # Print audit trail summary
    data = audit.to_dict()
    print("Audit Trail Summary")
    print("=" * 60)
    print(f"  Evaluation ID: {data['evaluation_id']}")
    print(f"  Total entries: {data['summary']['total_entries']}")
    print(f"  Passes:        {data['summary']['passes']}")
    print(f"  Failures:      {data['summary']['failures']}")
    print(f"  Layers:        {', '.join(data['summary']['layers_covered'])}")

    print(f"\n{'=' * 60}")
    print("Audit Entries")
    print("=" * 60)
    for e in audit.entries:
        status = "PASS" if e.outcome == "pass" else ("FAIL" if e.outcome == "fail" else "INFO")
        print(f"  [{status:>4}] {e.layer:<16} {e.action:<30} {e.detail}")

    # Generate compliance report
    print(f"\n{'=' * 60}")
    report = generate_compliance_report(audit)
    print(report.to_markdown())

    # Save outputs
    audit.save_json()
    audit.save_markdown()
    print(f"Saved audit trail to .audit/{audit.evaluation_id}.json and .md")


if __name__ == "__main__":
    main()
