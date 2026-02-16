"""Phase 12: Demonstrate observability with telemetry and alerting.

Shows pipeline telemetry logging and alert evaluation.
The telemetry calls require a running LlamaStack server.
This example demonstrates the alerting system standalone.
"""

from src.observability.alerts import AlertCollector


def main():
    print("Observability Demo: Alert Evaluation")
    print("=" * 60)

    collector = AlertCollector(
        shield_violation_threshold=2,
        policy_denial_threshold=3,
        low_score_threshold=3.0,
    )

    # Simulate events from a pipeline run
    print("\nSimulating pipeline events...")

    # Shield results
    collector.record_shield_result("market", passed=True)
    print("  market shield: passed")
    collector.record_shield_result("tech", passed=True)
    print("  tech shield: passed")
    collector.record_shield_result("finance", passed=False)
    print("  finance shield: FAILED")
    collector.record_shield_result("risk", passed=False)
    print("  risk shield: FAILED")

    # Policy decisions
    collector.record_policy_decision("market", allowed=True)
    print("  market policy: allowed")
    collector.record_policy_decision("market", allowed=False)
    print("  market policy: DENIED")

    # Scores
    collector.record_score("market", 7.0)
    print("  market score: 7.0")
    collector.record_score("tech", 2.5)
    print("  tech score: 2.5")
    collector.record_score("finance", 6.0)
    print("  finance score: 6.0")
    collector.record_score("risk", 3.0)
    print("  risk score: 3.0")

    # Evaluate alerts
    print(f"\n{'=' * 60}")
    print("Alert Evaluation")
    print("=" * 60)
    alerts = collector.evaluate()

    if not alerts:
        print("  No alerts triggered")
    else:
        for alert in alerts:
            print(f"  [{alert.severity:>8}] {alert.rule}: {alert.message}")

    # Show telemetry usage example (requires LlamaStack server)
    print(f"\n{'=' * 60}")
    print("Telemetry API Usage (requires running LlamaStack server)")
    print("=" * 60)
    print("""
    from src.client import get_client
    from src.observability.pipeline_telemetry import PipelineTelemetry

    client = get_client()
    telemetry = PipelineTelemetry(client)

    telemetry.start("My startup idea...")
    span_id = telemetry.start_span("market_evaluation")
    telemetry.log("Running market analysis", severity="info")
    telemetry.metric("agent_score", 7.5, "score")
    telemetry.log_shield_result("prompt-guard", "market", passed=True)
    telemetry.end_span(span_id)
    telemetry.end()

    # Query the trace
    trace = telemetry.get_trace()
    """)


if __name__ == "__main__":
    main()
