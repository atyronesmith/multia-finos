#!/bin/bash
# Pull required Ollama models (local or remote)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env if present
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"

MODELS=(
    "llama3.1:8b"
    "llama3.2:3b"
    "nomic-embed-text"
)

echo "Ollama: $OLLAMA_URL"
echo ""

# Check if Ollama is reachable
if ! curl -s "$OLLAMA_URL" > /dev/null 2>&1; then
    echo "Error: Cannot reach Ollama at $OLLAMA_URL"
    echo "Make sure Ollama is running."
    exit 1
fi

# Get already-installed models
installed=$(curl -s "$OLLAMA_URL/api/tags" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('models', []):
    print(m['name'])
" 2>/dev/null)

for model in "${MODELS[@]}"; do
    if echo "$installed" | grep -q "^${model}"; then
        echo "✓ $model (already pulled)"
    else
        echo "Pulling $model..."
        if [ "$OLLAMA_URL" = "http://localhost:11434" ]; then
            ollama pull "$model"
        else
            curl -s "$OLLAMA_URL/api/pull" -d "{\"name\": \"$model\"}" | \
                python3 -c "
import sys, json
for line in sys.stdin:
    data = json.loads(line)
    status = data.get('status', '')
    if 'pulling' in status or 'verifying' in status or 'success' in status:
        print(f'  {status}')
"
        fi
    fi
done

echo ""
echo "Done."
