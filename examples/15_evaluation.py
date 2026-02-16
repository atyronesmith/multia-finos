"""Phase 13: Demonstrate LLM-as-Judge evaluation and bias detection.

The scoring API calls require a running LlamaStack server.
This example demonstrates bias detection standalone.
"""

from src.evaluation.bias_detector import detect_bias


def main():
    print("Evaluation Demo: Bias Detection")
    print("=" * 60)

    # Simulated history of evaluation runs
    score_history = [
        {
            "idea": "AI indoor farming platform",
            "scores": {"market": 7.0, "tech": 6.5, "finance": 7.0, "risk": 6.0},
            "recommendation": "GO",
        },
        {
            "idea": "Blockchain supply chain tracker",
            "scores": {"market": 7.5, "tech": 7.0, "finance": 6.5, "risk": 6.5},
            "recommendation": "GO",
        },
        {
            "idea": "AR furniture shopping app",
            "scores": {"market": 6.0, "tech": 6.5, "finance": 7.0, "risk": 6.0},
            "recommendation": "GO",
        },
        {
            "idea": "Quantum computing SaaS",
            "scores": {"market": 3.0, "tech": 2.0, "finance": 3.5, "risk": 2.5},
            "recommendation": "NO-GO",
        },
    ]

    print(f"\nAnalyzing {len(score_history)} evaluation runs...\n")
    report = detect_bias(score_history)

    for check in report.checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  [{status}] {check['name']}: {check['detail']}")

    print(f"\nBias detected: {report.bias_detected}")

    # Test with skewed data
    print(f"\n{'=' * 60}")
    print("Skewed Dataset (all GO recommendations)")
    print("=" * 60)

    skewed_history = [
        {"idea": f"Idea {i}", "scores": {"market": 7.0, "tech": 7.0, "finance": 7.0, "risk": 7.0}, "recommendation": "GO"}
        for i in range(5)
    ]
    report = detect_bias(skewed_history)

    for check in report.checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  [{status}] {check['name']}: {check['detail']}")

    print(f"\nBias detected: {report.bias_detected}")

    # Show scoring API usage (requires LlamaStack server)
    print(f"\n{'=' * 60}")
    print("LLM-as-Judge Scoring (requires running LlamaStack server)")
    print("=" * 60)
    print("""
    from src.client import get_client
    from src.pipeline import run_pipeline
    from src.evaluation.evaluator import evaluate_report

    client = get_client()
    state = run_pipeline(client, "My startup idea...")
    result = evaluate_report(client, state)

    print(f"Scores: {result.scores}")
    print(f"Average: {result.average:.1f}")
    print(f"Needs review: {result.needs_review}")
    """)


if __name__ == "__main__":
    main()
