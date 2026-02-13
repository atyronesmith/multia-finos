#!/bin/bash
# Install venv and all dependencies needed to run the LlamaStack server.
# Run this once on any machine that will host the server.
# Safe to re-run -- it will skip steps that are already done.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Installing LlamaStack server ==="
echo "Project: $PROJECT_DIR"
echo ""

# 1. Create venv if missing
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_DIR/.venv"
else
    echo "Virtual environment already exists."
fi
source "$PROJECT_DIR/.venv/bin/activate"

# 2. Upgrade pip
pip install --upgrade pip --quiet

# 3. Install all server dependencies
echo "Installing dependencies..."
pip install \
    llama-stack \
    llama-stack-client \
    fire \
    requests \
    python-dotenv \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-exporter-otlp-proto-http \
    aiosqlite \
    ollama \
    litellm \
    sqlalchemy \
    greenlet \
    faiss-cpu \
    mcp \
    --quiet

# 4. Install the project itself
pip install -e "$PROJECT_DIR" --quiet

# 5. Create data directories
mkdir -p ~/.llama/distributions/multia

# 6. Create .env from example if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "Created .env from .env.example -- edit it to configure remote Ollama, etc."
fi

# 7. Verify Python imports
echo ""
echo "Verifying Python installation..."
"$PROJECT_DIR/.venv/bin/python" -c "
from llama_stack.distribution.server.server import main
from src.config import OLLAMA_URL, LLAMASTACK_URL
print(f'  LlamaStack server: OK')
print(f'  Ollama URL:        {OLLAMA_URL}')
print(f'  LlamaStack URL:    {LLAMASTACK_URL}')
"

# 8. Check Ollama connectivity and models
echo ""
echo "Checking Ollama..."

# Load .env for OLLAMA_URL
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"

REQUIRED_MODELS=("llama3.1:8b" "llama3.2:3b" "nomic-embed-text")

if ! curl -sf "$OLLAMA_URL" > /dev/null 2>&1; then
    echo "  WARNING: Cannot reach Ollama at $OLLAMA_URL"
    echo "  Make sure Ollama is running, then run: ./scripts/pull_models.sh"
else
    echo "  Ollama reachable at $OLLAMA_URL"

    # Check which models are installed (list full names like "llama3.1:8b", "nomic-embed-text:latest")
    installed=$(curl -s "$OLLAMA_URL/api/tags" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('models', []):
    print(m['name'])
" 2>/dev/null)

    missing=()
    for model in "${REQUIRED_MODELS[@]}"; do
        # Match "model" as-is or "model:latest" for models without explicit tags
        if echo "$installed" | grep -q "^${model}\b"; then
            echo "  ✓ $model"
        else
            echo "  ✗ $model (not found)"
            missing+=("$model")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        echo ""
        read -p "Pull missing models? [Y/n] " answer
        answer="${answer:-Y}"
        if [[ "$answer" =~ ^[Yy]$ ]]; then
            for model in "${missing[@]}"; do
                echo "  Pulling $model..."
                if [ "$OLLAMA_URL" = "http://localhost:11434" ]; then
                    ollama pull "$model"
                else
                    curl -s "$OLLAMA_URL/api/pull" -d "{\"name\": \"$model\"}" | \
                        python3 -c "
import sys, json
for line in sys.stdin:
    data = json.loads(line)
    status = data.get('status', '')
    if status:
        print(f'    {status}')
" 2>/dev/null
                fi
            done

            # Verify after pull
            echo ""
            echo "  Verifying models..."
            installed=$(curl -s "$OLLAMA_URL/api/tags" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('models', []):
    print(m['name'].split(':')[0] + ':' + m['name'].split(':')[-1] if ':' in m['name'] else m['name'])
" 2>/dev/null)

            all_ok=true
            for model in "${REQUIRED_MODELS[@]}"; do
                if echo "$installed" | grep -q "^${model}$"; then
                    echo "  ✓ $model"
                else
                    echo "  ✗ $model FAILED"
                    all_ok=false
                fi
            done

            if [ "$all_ok" = false ]; then
                echo ""
                echo "  WARNING: Some models failed to pull. Check Ollama logs."
            fi
        else
            echo "  Skipped. Run ./scripts/pull_models.sh later."
        fi
    fi
fi

echo ""
echo "=== Done ==="
echo "Start server: ./scripts/start_server.sh"
