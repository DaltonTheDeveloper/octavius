#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv (fast Python package manager)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

uv venv
uv pip install -e .

echo
echo "Installed. To run:"
echo "  source .venv/bin/activate"
echo "  octavius-bus"
echo
echo "Then add it to Claude Code:"
echo "  claude mcp add --transport http octavius http://127.0.0.1:7777/mcp"
