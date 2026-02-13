#!/bin/bash
# Start the FastAPI gateway
# Reads GATEWAY_HOST and GATEWAY_PORT from .env or environment
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

source "$PROJECT_DIR/.venv/bin/activate"

# Load .env if present
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

GATEWAY_HOST="${GATEWAY_HOST:-0.0.0.0}"
GATEWAY_PORT="${GATEWAY_PORT:-8080}"

echo "Gateway: http://$GATEWAY_HOST:$GATEWAY_PORT"
echo ""

uvicorn src.gateway.server:app --host "$GATEWAY_HOST" --port "$GATEWAY_PORT"
