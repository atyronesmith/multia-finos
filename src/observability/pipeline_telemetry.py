"""Thin wrapper around LlamaStack Telemetry API for pipeline-specific events."""

import uuid
from datetime import datetime, timezone

from llama_stack_client import LlamaStackClient

DEFAULT_TTL = 86400  # 24 hours


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


class PipelineTelemetry:
    """Scoped telemetry helper for a single pipeline run.

    Creates a trace with a root span, and provides methods to log
    events and metrics within that trace.
    """

    def __init__(self, client: LlamaStackClient, ttl_seconds: int = DEFAULT_TTL):
        self.client = client
        self.ttl_seconds = ttl_seconds
        self.trace_id = _new_id()
        self.root_span_id = _new_id()
        self._started = False

    def start(self, startup_idea: str):
        """Start the pipeline trace with a root span."""
        self.client.telemetry.log_event(
            event={
                "type": "structured_log",
                "payload": {"type": "span_start", "name": "pipeline_run"},
                "trace_id": self.trace_id,
                "span_id": self.root_span_id,
                "timestamp": _now_iso(),
                "attributes": {"startup_idea": startup_idea},
            },
            ttl_seconds=self.ttl_seconds,
        )
        self._started = True

    def end(self, status: str = "ok"):
        """End the pipeline root span."""
        self.client.telemetry.log_event(
            event={
                "type": "structured_log",
                "payload": {"type": "span_end", "status": status},
                "trace_id": self.trace_id,
                "span_id": self.root_span_id,
                "timestamp": _now_iso(),
            },
            ttl_seconds=self.ttl_seconds,
        )

    def start_span(self, name: str, attributes: dict | None = None) -> str:
        """Start a child span and return its span_id."""
        span_id = _new_id()
        self.client.telemetry.log_event(
            event={
                "type": "structured_log",
                "payload": {
                    "type": "span_start",
                    "name": name,
                    "parent_span_id": self.root_span_id,
                },
                "trace_id": self.trace_id,
                "span_id": span_id,
                "timestamp": _now_iso(),
                "attributes": attributes or {},
            },
            ttl_seconds=self.ttl_seconds,
        )
        return span_id

    def end_span(self, span_id: str, status: str = "ok"):
        """End a child span."""
        self.client.telemetry.log_event(
            event={
                "type": "structured_log",
                "payload": {"type": "span_end", "status": status},
                "trace_id": self.trace_id,
                "span_id": span_id,
                "timestamp": _now_iso(),
            },
            ttl_seconds=self.ttl_seconds,
        )

    def log(self, message: str, severity: str = "info", attributes: dict | None = None):
        """Log an unstructured message within the pipeline trace."""
        self.client.telemetry.log_event(
            event={
                "type": "unstructured_log",
                "message": message,
                "severity": severity,
                "trace_id": self.trace_id,
                "span_id": self.root_span_id,
                "timestamp": _now_iso(),
                "attributes": attributes or {},
            },
            ttl_seconds=self.ttl_seconds,
        )

    def metric(self, name: str, value: float, unit: str, attributes: dict | None = None):
        """Log a metric event within the pipeline trace."""
        self.client.telemetry.log_event(
            event={
                "type": "metric",
                "metric": name,
                "value": value,
                "unit": unit,
                "trace_id": self.trace_id,
                "span_id": self.root_span_id,
                "timestamp": _now_iso(),
                "attributes": attributes or {},
            },
            ttl_seconds=self.ttl_seconds,
        )

    def log_policy_decision(self, agent_name: str, tool_name: str, allowed: bool, reason: str):
        """Log a policy decision from the governance engine."""
        self.log(
            f"Policy decision: agent={agent_name} tool={tool_name} allowed={allowed}",
            severity="warn" if not allowed else "info",
            attributes={
                "event_type": "policy_decision",
                "agent_name": agent_name,
                "tool_name": tool_name,
                "allowed": allowed,
                "reason": reason,
            },
        )

    def log_shield_result(self, shield_id: str, agent_name: str, passed: bool, message: str = ""):
        """Log a shield gate result."""
        self.log(
            f"Shield result: shield={shield_id} agent={agent_name} passed={passed}",
            severity="warn" if not passed else "info",
            attributes={
                "event_type": "shield_result",
                "shield_id": shield_id,
                "agent_name": agent_name,
                "passed": passed,
                "message": message,
            },
        )

    def get_trace(self) -> dict:
        """Query the span tree for this pipeline's trace."""
        return self.client.telemetry.get_span_tree(
            self.root_span_id,
            max_depth=10,
        )


def query_recent_traces(client: LlamaStackClient, limit: int = 10):
    """Query the most recent traces from telemetry."""
    return client.telemetry.query_traces(limit=limit)
