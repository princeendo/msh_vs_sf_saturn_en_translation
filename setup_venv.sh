#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v uv >/dev/null 2>&1; then
    printf 'error: uv is required; install it from https://docs.astral.sh/uv/\n' >&2
    exit 127
fi

exec uv sync --project "$ROOT_DIR" --all-groups
