#!/bin/zsh

set -e

KERNEL="confidentialnvidia/confidential-mi-agent-007"

echo
echo "=============================================="
echo "MI BOND / AGENT 007 — KAGGLE WAKE"
echo "=============================================="
echo
echo "Kernel:"
echo "$KERNEL"
echo

if ! command -v kaggle >/dev/null 2>&1; then
    echo "ERROR: Kaggle CLI is not installed."
    exit 1
fi

echo "Kaggle CLI:"
kaggle --version

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/mi-bond-wake.XXXXXX")"

cleanup() {
    rm -rf "$TMP_DIR"
}

trap cleanup EXIT INT TERM

echo
echo "Downloading current MI BOND notebook..."
echo

kaggle kernels pull \
    "$KERNEL" \
    -p "$TMP_DIR" \
    -m

echo
echo "Downloaded files:"
ls -la "$TMP_DIR"

if [ ! -f "$TMP_DIR/kernel-metadata.json" ]; then
    echo
    echo "ERROR: kernel-metadata.json was not downloaded."
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

expected = (
    "confidentialnvidia/"
    "confidential-mi-agent-007"
)

actual = data.get("id", "")

print()
print("Kernel metadata ID:")
print(actual)

if actual != expected:
    raise SystemExit(
        "ERROR: Refusing to push. "
        f"Expected {expected!r}, got {actual!r}"
    )

print("Metadata verified.")
PY

echo
echo "=============================================="
echo "TRIGGERING MI BOND KAGGLE RUN"
echo "=============================================="

kaggle kernels push \
    -p "$TMP_DIR"

echo
echo "Wake request submitted."
echo
echo "=============================================="
echo "WATCHING AGENT 007 STATUS"
echo "=============================================="

for i in $(seq 1 40); do

    echo
    echo "Status check $i / 40"

    STATUS="$(
        kaggle kernels status \
        "$KERNEL" \
        2>&1 || true
    )"

    echo "$STATUS"

    LOWER="$(
        printf '%s' "$STATUS" |
        tr '[:upper:]' '[:lower:]'
    )"

    if printf '%s' "$LOWER" | grep -q "error"; then
        echo
        echo "ERROR: MI BOND Kaggle notebook entered an error state."
        exit 1
    fi

    if printf '%s' "$LOWER" | grep -q "cancel"; then
        echo
        echo "ERROR: MI BOND Kaggle notebook was cancelled."
        exit 1
    fi

    if printf '%s' "$LOWER" | grep -q "running"; then
        echo
        echo "=============================================="
        echo "AGENT 007 KAGGLE WORKER IS RUNNING"
        echo "=============================================="
        exit 0
    fi

    if printf '%s' "$LOWER" | grep -q "complete"; then
        echo
        echo "Notebook completed."
        echo "Check whether its worker/tunnel remains alive."
        exit 0
    fi

    sleep 15
done

echo
echo "Timed out waiting for a final Kaggle status."
exit 1
