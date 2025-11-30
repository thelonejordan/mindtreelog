#!/usr/bin/env bash
set -euo pipefail

# Check if uv.lock is in sync with pyproject.toml

echo "Checking if uv.lock is in sync with pyproject.toml..."

# Run uv lock --check to verify lock file is up to date
if uv lock --check; then
    echo "✅ uv.lock is in sync with pyproject.toml"
    exit 0
else
    echo "❌ uv.lock is out of sync with pyproject.toml"
    echo ""
    echo "💡 Run the following command to update the lock file:"
    echo "   uv lock"
    echo ""
    exit 1
fi
