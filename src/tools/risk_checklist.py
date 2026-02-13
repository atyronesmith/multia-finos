"""Risk checklist tool for structured risk assessment."""

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "risk_templates.json"


def _load_templates() -> dict:
    with open(DATA_FILE) as f:
        return json.load(f)


def risk_checklist(category: str) -> str:
    """Get a structured risk checklist for a specific risk category.
    Use this tool to systematically evaluate risks in a given area.

    :param category: The risk category to assess. Options: market, technology, financial, regulatory, team, operational
    :returns: A checklist of risk factors to evaluate for the given category
    """
    templates = _load_templates()
    category_lower = category.lower().strip()

    if category_lower in templates:
        checklist = templates[category_lower]
    else:
        available = ", ".join(templates.keys())
        return f"Unknown category '{category}'. Available categories: {available}"

    lines = [f"Risk Checklist: {category.upper()}"]
    lines.append("-" * 40)
    for item in checklist:
        lines.append(f"- [ ] {item['risk']}")
        lines.append(f"      Impact: {item['impact']} | Likelihood: {item['likelihood']}")
    return "\n".join(lines)
