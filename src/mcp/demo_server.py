"""Demo MCP server with market sentiment and funding lookup tools.

Uses FastMCP with SSE transport. Run with:
    python -m src.mcp.demo_server
or:
    ./scripts/start_mcp_demo.sh
"""

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

mcp = FastMCP("multia-demo", host="0.0.0.0", port=int(os.getenv("MCP_DEMO_PORT", "8888")))


@mcp.tool()
def market_sentiment(industry: str) -> str:
    """Get market sentiment analysis for a given industry.

    Args:
        industry: Industry name (e.g. fintech, healthtech, agtech, ai infrastructure)
    """
    data = json.loads((DATA_DIR / "mcp_market_sentiment.json").read_text())
    for entry in data:
        if entry["industry"].lower() == industry.lower():
            return json.dumps(entry, indent=2)
    industries = [e["industry"] for e in data]
    return json.dumps({"error": f"Industry '{industry}' not found", "available": industries})


@mcp.tool()
def funding_lookup(company_name: str) -> str:
    """Look up funding data for a startup company.

    Args:
        company_name: Company name (e.g. Stripe, Plaid, Scale AI)
    """
    data = json.loads((DATA_DIR / "mcp_funding_data.json").read_text())
    for entry in data:
        if entry["company"].lower() == company_name.lower():
            return json.dumps(entry, indent=2)
    companies = [e["company"] for e in data]
    return json.dumps({"error": f"Company '{company_name}' not found", "available": companies})


if __name__ == "__main__":
    mcp.run(transport="sse")
