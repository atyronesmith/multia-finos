#!/usr/bin/env python3
"""Query and display recent traces from the LlamaStack Telemetry API.

Requires a running LlamaStack server.

Usage:
    python scripts/view_traces.py [--limit N]
"""

import argparse

from src.client import get_client
from src.observability.pipeline_telemetry import query_recent_traces


def main():
    parser = argparse.ArgumentParser(description="View recent LlamaStack traces")
    parser.add_argument("--limit", type=int, default=10, help="Number of traces to show")
    args = parser.parse_args()

    client = get_client()
    traces = query_recent_traces(client, limit=args.limit)

    if not traces:
        print("No traces found.")
        return

    print(f"Recent traces (showing up to {args.limit}):")
    print("=" * 80)
    for trace in traces:
        print(f"  Trace ID:   {trace.trace_id}")
        print(f"  Root Span:  {trace.root_span_id}")
        print(f"  Started:    {trace.start_time}")
        end = trace.end_time or "in progress"
        print(f"  Ended:      {end}")

        # Get span tree for this trace
        try:
            tree = client.telemetry.get_span_tree(trace.root_span_id, max_depth=5)
            if hasattr(tree, "__iter__"):
                span_count = sum(1 for _ in tree) if not isinstance(tree, dict) else len(tree)
                print(f"  Spans:      {span_count}")
        except Exception:
            print("  Spans:      (unable to retrieve)")

        print("-" * 80)


if __name__ == "__main__":
    main()
