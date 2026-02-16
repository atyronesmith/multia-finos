"""Statistical bias detection across multiple evaluation runs."""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class BiasReport:
    checks: list[dict] = field(default_factory=list)
    bias_detected: bool = False

    def add_check(self, name: str, passed: bool, detail: str):
        self.checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            self.bias_detected = True


def detect_bias(score_history: list[dict]) -> BiasReport:
    """Analyze a list of evaluation score records for bias patterns.

    Each record should have:
        - "idea": str
        - "scores": dict[str, float]  (agent_name -> score)
        - "recommendation": str
    """
    report = BiasReport()

    if len(score_history) < 2:
        report.add_check(
            "sample_size",
            passed=True,
            detail=f"Only {len(score_history)} evaluation(s) — insufficient for bias detection",
        )
        return report

    # Check 1: Score range — are all scores suspiciously similar?
    all_scores = []
    for record in score_history:
        all_scores.extend(record.get("scores", {}).values())

    if all_scores:
        score_range = max(all_scores) - min(all_scores)
        narrow_range = score_range < 1.5
        report.add_check(
            "score_range",
            passed=not narrow_range,
            detail=f"Score range: {score_range:.1f} ({'narrow — possible anchoring bias' if narrow_range else 'acceptable variation'})",
        )

    # Check 2: Recommendation skew — is the system always saying GO or NO-GO?
    recommendations = [r.get("recommendation", "") for r in score_history]
    go_count = sum(1 for r in recommendations if r == "GO")
    nogo_count = sum(1 for r in recommendations if r == "NO-GO")
    total = go_count + nogo_count

    if total >= 3:
        skew_ratio = max(go_count, nogo_count) / total
        skewed = skew_ratio > 0.85
        report.add_check(
            "recommendation_skew",
            passed=not skewed,
            detail=f"GO={go_count} NO-GO={nogo_count} ({skew_ratio:.0%} skew{'ed — possible confirmation bias' if skewed else ''})",
        )

    # Check 3: Agent consistency — does one agent always score high/low?
    agent_scores: dict[str, list[float]] = {}
    for record in score_history:
        for agent, score in record.get("scores", {}).items():
            agent_scores.setdefault(agent, []).append(score)

    for agent, scores in agent_scores.items():
        if len(scores) >= 2:
            avg = sum(scores) / len(scores)
            variance = sum((s - avg) ** 2 for s in scores) / len(scores)
            low_variance = variance < 0.5 and len(scores) >= 3
            report.add_check(
                f"agent_{agent}_variance",
                passed=not low_variance,
                detail=f"{agent}: avg={avg:.1f} var={variance:.1f} ({'low variance — possible systematic bias' if low_variance else 'ok'})",
            )

    return report
