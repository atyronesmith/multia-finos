#!/bin/bash
# Check that the venv and client dependencies are installed.
# For full server install, use install_server.sh instead.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "No .venv found. Run ./scripts/install_server.sh first."
    exit 1
fi
source "$PROJECT_DIR/.venv/bin/activate"

DEPS=(
    "llama-stack-client"
    "python-dotenv"
)

missing=()
for dep in "${DEPS[@]}"; do
    if ! pip show "$dep" > /dev/null 2>&1; then
        missing+=("$dep")
    fi
done

if [ ${#missing[@]} -eq 0 ]; then
    echo "All client dependencies installed."
else
    echo "Missing: ${missing[*]}"
    echo "Run ./scripts/install_server.sh to install everything."
    exit 1
fi
