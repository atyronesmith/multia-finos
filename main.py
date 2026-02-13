"""CLI entry point for the multi-agent startup evaluator."""

import sys

from src.client import get_client
from src.pipeline import run_pipeline


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<startup idea>\"")
        print()
        print("Example:")
        print('  python main.py "An AI platform that optimizes indoor farming"')
        sys.exit(1)

    idea = " ".join(sys.argv[1:])
    client = get_client()
    state = run_pipeline(client, idea)

    print(f"\nFinal recommendation: {state.recommendation}")
    print(f"Average score: {state.average_score:.1f}/10")


if __name__ == "__main__":
    main()
