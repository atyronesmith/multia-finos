#!/bin/bash
# Start LlamaStack server with Ollama backend
# Reads OLLAMA_URL and LLAMASTACK_PORT from .env or environment
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

source "$PROJECT_DIR/.venv/bin/activate"

# Load .env if present
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
LLAMASTACK_PORT="${LLAMASTACK_PORT:-8321}"
LLAMASTACK_HOST="${LLAMASTACK_HOST:-0.0.0.0}"

mkdir -p ~/.llama/distributions/multia

# Generate run config with current OLLAMA_URL
CONFIG="$PROJECT_DIR/config/run.yaml"
sed "s|url: http://localhost:11434|url: ${OLLAMA_URL}|" "$CONFIG" > /tmp/multia_run.yaml

echo "Ollama URL:      $OLLAMA_URL"
echo "LlamaStack:      $LLAMASTACK_HOST:$LLAMASTACK_PORT"
echo ""

llama stack run /tmp/multia_run.yaml --port "$LLAMASTACK_PORT"
