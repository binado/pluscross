#!/usr/bin/env bash
# Cross-language round trips: python-writes→julia-reads and julia-writes→python-reads.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
repo="$(dirname "$(dirname "$here")")"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

py() {
    (cd "$repo/python" && PYTHONPATH="$here" uv run --project . python "$here/$1" "$2")
}
jl() {
    julia --project="$repo/julia/PlusCross" "$here/$1" "$2"
}

echo "== python writes, julia reads =="
py write_catalog.py "$tmp/py_catalog.h5"
jl check_catalog.jl "$tmp/py_catalog.h5"

echo "== julia writes, python reads =="
jl write_catalog.jl "$tmp/jl_catalog.h5"
py check_catalog.py "$tmp/jl_catalog.h5"

echo "cross-language round trips OK"
