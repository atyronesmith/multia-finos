"""Market data tool for searching comparable startups."""

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "comparables.json"


def _load_comparables() -> list[dict]:
    with open(DATA_FILE) as f:
        return json.load(f)


def search_comparables(industry: str) -> str:
    """Search for comparable startups in a given industry or market sector.
    Use this tool to find existing companies, their funding, revenue,
    and outcomes to benchmark a new startup idea against.

    :param industry: The industry or market sector to search for, e.g. 'fintech', 'healthtech', 'agtech'
    :returns: JSON string with a list of comparable startups and their metrics
    """
    comparables = _load_comparables()
    matches = [
        c for c in comparables
        if industry.lower() in c.get("industry", "").lower()
        or industry.lower() in c.get("tags", "")
    ]
    if not matches:
        matches = comparables[:3]
        return json.dumps({
            "query": industry,
            "note": "No exact matches found. Showing sample comparables.",
            "results": matches,
        }, indent=2)
    return json.dumps({
        "query": industry,
        "results": matches,
    }, indent=2)
