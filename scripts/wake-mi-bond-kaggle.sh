#!/bin/zsh

set -e

KERNEL="confidentialnvidia/confidential-mi-agent-007"

echo
echo "===================================================="
echo "MI BOND / AGENT 007 — KAGGLE WAKE"
echo "===================================================="

echo
echo "Target Kaggle notebook:"
echo "$KERNEL"

if ! command -v kaggle >/dev/null 2>&1; then
    echo
    echo "Kaggle CLI not found."

    if command -v python3 >/dev/null 2>&1; then
        echo "Installing Kaggle CLI..."
        python3 -m pip install -U kaggle
    else
        echo "ERROR: Python 3 is not available."
        exit 1
    fi
fi

echo
echo "Kaggle CLI:"
kaggle --version

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/mi-bond-agent007-wake.XXXXXX")"

cleanup() {
    rm -rf "$TMP_DIR"
}

trap cleanup EXIT INT TERM

echo
echo "===================================================="
echo "PULL CURRENT AGENT 007 NOTEBOOK"
echo "===================================================="

kaggle kernels pull \
    "$KERNEL" \
    -p "$TMP_DIR" \
    -m

echo
echo "Downloaded:"
ls -la "$TMP_DIR"

if [ ! -f "$TMP_DIR/kernel-metadata.json" ]; then
    echo
    echo "ERROR: Kaggle metadata was not downloaded."
    exit 1
fi

python3 - "$TMP_DIR/kernel-metadata.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])

data = json.loads(
    path.read_text(
        encoding="utf-8"
    )
)

expected = "confidentialnvidia/confidential-mi-agent-007"
actual = data.get("id", "")

print()
print("Metadata kernel ID:")
print(actual)

if actual != expected:
    raise SystemExit(
        f"ERROR: Expected {expected!r}, got {actual!r}"
    )

print("Agent 007 notebook verified.")
PY

echo
echo "===================================================="
echo "TRIGGER KAGGLE RUN"
echo "===================================================="

kaggle kernels push \
    -p "$TMP_DIR"

echo
echo "Wake request submitted."

echo
echo "===================================================="
echo "WATCH KAGGLE STATUS"
echo "===================================================="

SUCCESS=0

for i in $(seq 1 40); do

    echo
    echo "Status check $i / 40"

    STATUS="$(
        kaggle kernels status "$KERNEL" 2>&1 || true
    )"

    echo "$STATUS"

    LOWER="$(
        printf '%s' "$STATUS" |
        tr '[:upper:]' '[:lower:]'
    )"

    if printf '%s' "$LOWER" | grep -q "error"; then
        echo
        echo "ERROR: Agent 007 Kaggle notebook entered error state."
        exit 1
    fi

    if printf '%s' "$LOWER" | grep -q "cancel"; then
        echo
        echo "ERROR: Agent 007 Kaggle notebook was cancelled."
        exit 1
    fi

    if printf '%s' "$LOWER" | grep -q "running"; then
        echo
        echo "===================================================="
        echo "AGENT 007 KAGGLE NOTEBOOK IS RUNNING"
        echo "===================================================="
        SUCCESS=1
        break
    fi

    if printf '%s' "$LOWER" | grep -q "complete"; then
        echo
        echo "Kaggle notebook completed."
        SUCCESS=1
        break
    fi

    sleep 15
done

if [ "$SUCCESS" -ne 1 ]; then
    echo
    echo "ERROR: Timed out waiting for Agent 007 Kaggle status."
    exit 1
fi

echo
echo "Temporary wake copy removed automatically."
