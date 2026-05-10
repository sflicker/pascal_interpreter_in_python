#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${ROOT_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 [--debug] [--verbose] [--trace-tokens] [--trace-source] [--trace-all] path/to/program.pas" >&2
    exit 2
fi

python3 -m pascal_interpreter "$@"
