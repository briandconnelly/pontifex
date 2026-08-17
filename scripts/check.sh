#!/usr/bin/env bash
# The full verification gate. CI runs this exact script (.github/workflows/test.yml),
# so a green run here is a green run there. Documented in CONTRIBUTING.md#the-gate.
#
# Usage:
#   uv run scripts/check.sh
#
# Environment:
#   SKIP_WHEEL_CHECK=1   skip the packaging step while iterating locally. CI never
#                        sets this; the step catches missing package data and import
#                        errors that only appear in a built wheel.
set -euo pipefail

cd "$(dirname "$0")/.."

step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }

step "Locked install"
uv sync --frozen

step "GitHub Actions are SHA-pinned"
uv run python scripts/check_github_actions_pinning.py

step "Lint"
uv run ruff check .

step "Format"
uv run ruff format --check .

step "Type check"
uv run ty check

step "One-way core dependency rule"
uv run lint-imports

step "Tests (95% coverage floor)"
uv run pytest

if [[ -n "${SKIP_WHEEL_CHECK:-}" ]]; then
  step "Wheel check SKIPPED (SKIP_WHEEL_CHECK is set)"
else
  step "Wheel builds and imports without test deps"
  # Build into a fresh temp directory, never into ./dist: a persistent dist/ can hold
  # wheels from earlier builds (including pre-rename `pontifex` ones), and a glob over
  # it would expand to several paths where exactly one is expected.
  wheel_dir="$(mktemp -d)"
  trap 'rm -rf "$wheel_dir"' EXIT
  uv build --wheel --out-dir "$wheel_dir"
  wheel_count=$(find "$wheel_dir" -name '*.whl' | wc -l | tr -d ' ')
  if [[ "$wheel_count" != "1" ]]; then
    echo "expected exactly 1 built wheel, found ${wheel_count} in ${wheel_dir}" >&2
    exit 1
  fi
  wheel="$(find "$wheel_dir" -name '*.whl')"
  uv run --isolated --no-project --with "$wheel" \
    python -c "import pontonier.core.jobs, pontonier.core.worktree; import pontonier; print(pontonier.__version__)"
fi

printf '\n\033[1;32m==> gate passed\033[0m\n'
