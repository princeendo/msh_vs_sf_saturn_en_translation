#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v uv >/dev/null 2>&1; then
    printf 'error: uv is required; run ./setup_venv.sh after installing uv\n' >&2
    exit 127
fi

if [[ $# -eq 0 ]]; then
    printf 'usage: %s COMMAND [ARG ...]\n' "$0" >&2
    exit 2
fi

exec uv run --project "$ROOT_DIR" "$@"
