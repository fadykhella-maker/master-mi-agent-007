#!/bin/zsh
set -e

SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
STAGE_DIR="$HOME/MI-Reflex/mi-agent-007"

echo ""
echo "MI BOND · Agent 007"
echo "==================="
echo "Source:  $SOURCE_DIR"
echo "Runtime: $STAGE_DIR"
echo ""

mkdir -p "$STAGE_DIR"

rsync -a --delete \
  --exclude '.git' \
  --exclude '.web' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  "$SOURCE_DIR/" "$STAGE_DIR/"

cd "$STAGE_DIR"

if [ ! -d ".venv" ]; then
    uv venv --python 3.12
fi

source .venv/bin/activate

uv pip install -r requirements.txt >/dev/null

echo ""
echo "Launching MI BOND..."
echo "http://localhost:3000"
echo ""

uv run reflex run
