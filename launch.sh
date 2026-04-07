#!/usr/bin/env bash
# FreedomForge AI — launcher
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$DIR/.venv"

if [[ ! -d "$VENV" ]]; then
    echo ""
    echo "  ❌  Virtual environment not found."
    echo "      Please run the installer first:"
    echo ""
    echo "        bash \"$DIR/install.sh\""
    echo ""
    exit 1
fi

source "$VENV/bin/activate"
exec python3 "$DIR/main.py" "$@"
