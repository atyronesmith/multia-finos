"""Simple alerting rules based on telemetry events."""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    rule: str
    severity: str  # info, warn, critical
    message: str


@dataclass
class AlertCollector:
    """Collects events and evaluates alerting rules at the end of a pipeline run."""

    shield_violation_threshold: int = 2
    policy_denial_threshold: int = 3
    low_score_threshold: float = 3.0

    _shield_violations: int = 0
    _policy_denials: int = 0
    _low_scores: list[str] = field(default_factory=list)
    alerts: list[Alert] = field(default_factory=list)

    def record_shield_result(self, agent_name: str, passed: bool):
        if not passed:
            self._shield_violations += 1

    def record_policy_decision(self, agent_name: str, allowed: bool):
        if not allowed:
            self._policy_denials += 1

    def record_score(self, agent_name: str, score: float):
        if score <= self.low_score_threshold:
            self._low_scores.append(agent_name)

    def evaluate(self) -> list[Alert]:
        """Evaluate all alerting rules and return any triggered alerts."""
        self.alerts = []

        if self._shield_violations >= self.shield_violation_threshold:
            alert = Alert(
                rule="shield_violations",
                severity="critical",
                message=(
                    f"{self._shield_violations} shield violations detected "
                    f"(threshold: {self.shield_violation_threshold})"
                ),
            )
            self.alerts.append(alert)
            logger.critical("ALERT: %s", alert.message)

        if self._policy_denials >= self.policy_denial_threshold:
            alert = Alert(
                rule="policy_denials",
                severity="warn",
                message=(
                    f"{self._policy_denials} policy denials detected "
                    f"(threshold: {self.policy_denial_threshold})"
                ),
            )
            self.alerts.append(alert)
            logger.warning("ALERT: %s", alert.message)

        if self._low_scores:
            alert = Alert(
                rule="low_scores",
                severity="info",
                message=(
                    f"Low scores (≤{self.low_score_threshold}) from: "
                    f"{', '.join(self._low_scores)}"
                ),
            )
            self.alerts.append(alert)
            logger.info("ALERT: %s", alert.message)

        return self.alerts
