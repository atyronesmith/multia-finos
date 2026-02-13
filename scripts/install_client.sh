#!/bin/bash
# Install venv and dependencies needed to run the client (examples, main.py).
# Use this when LlamaStack server runs on a different machine.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Installing multia client ==="
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

# 3. Install client dependencies only
echo "Installing client dependencies..."
pip install \
    llama-stack-client \
    python-dotenv \
    --quiet

# 4. Install the project itself
pip install -e "$PROJECT_DIR" --quiet

# 5. Create .env from example if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "Created .env from .env.example"
fi

# 6. Verify
echo ""
echo "Verifying installation..."
"$PROJECT_DIR/.venv/bin/python" -c "
from src.config import LLAMASTACK_URL
print(f'  Client imports: OK')
print(f'  LlamaStack URL: {LLAMASTACK_URL}')
"

echo ""
echo "=== Done ==="
echo "Make sure LLAMASTACK_URL in .env points to your server."
echo "Then: source .venv/bin/activate && python examples/01_hello_agent.py"
