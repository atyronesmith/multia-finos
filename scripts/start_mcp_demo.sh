#!/bin/bash
# Start the demo MCP server (SSE transport)
# Reads MCP_DEMO_PORT from .env or environment (default: 8888)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

source "$PROJECT_DIR/.venv/bin/activate"

# Load .env if present
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

MCP_DEMO_PORT="${MCP_DEMO_PORT:-8888}"

echo "MCP Demo Server: http://0.0.0.0:$MCP_DEMO_PORT"
echo "Tools: market_sentiment, funding_lookup"
echo ""

python -m src.mcp.demo_server
