# Contributing

Repo-wide norms and off-limits actions live in [AGENTS.md](AGENTS.md). This file is
the procedure: how to set up, what the gate runs, and how to shape a commit.

## Setup

```sh
uv sync
prek install --hook-type commit-msg   # optional but recommended; see Commit messages
```

This project uses [uv](https://docs.astral.sh/uv/) for everything. Do not use pip,
poetry, or a `requirements.txt`.

## The gate

One command, run from the repository root. CI runs this exact script, so a green run
here is a green run there:

```sh
./scripts/check.sh
```

Run it directly rather than as `uv run scripts/check.sh` — the outer `uv run` would
lock and sync the project before the script starts, defeating its locked-install step.

It runs, in order:

| Step | Command |
| --- | --- |
| Locked install | `uv sync --locked` |
| Actions are SHA-pinned | `uv run python scripts/check_github_actions_pinning.py` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format --check .` |
| Types | `uv run ty check` |
| One-way core rule | `uv run lint-imports` |
| Tests + 95% coverage floor | `uv run pytest` |
| Wheel builds and imports clean | `uv build --wheel` into a temp dir, then import it |

The script exports `UV_LOCKED=1`, so any step that would rewrite `uv.lock` fails
instead. To iterate on one step, run it directly from the table. To skip the slow
packaging step, `SKIP_WHEEL_CHECK=1 ./scripts/check.sh`. CI never skips it.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/). The commit-msg hook in
`.pre-commit-config.yaml` enforces this via `scripts/check_commit_message.py`, which
takes its allowed values from this section — change them together.

```
type(scope)?!?: subject
```

- **types**: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`,
  `build`, `revert`
- **scopes** (optional): `core`, `backend`, `conventions`, `testing`, `packaging`,
  `release`, `changelog`, `ci`, `deps`
- **subject**: imperative, lowercase, no trailing period
- `!` marks a breaking change — required for anything the
  [freeze rules](AGENTS.md#rules) call breaking

Examples: `fix(core): confine job ids to the minted 32-hex shape`,
`feat(backend)!: freeze the backend protocol`.

## Pull requests

- Branch from `main` as `type/short-description`.
- Every behavior change updates `CHANGELOG.md` under an `## [Unreleased]` heading.
- Every behavior change that a doc describes updates that doc in the same PR.
- The `gate` check must pass. It is a required check, and it is not optional to
  bypass — see [docs/github-config.md](docs/github-config.md).
- A human reviews and merges. Agents do not merge or approve their own work.

## Docs

Each fact has one home. Before writing an explanation, check whether it already has
one and link instead. The homes are:

| Fact | Home |
| --- | --- |
| What each module is for | [README.md](README.md) |
| The one-way core import rule | `src/pontonier/core/__init__.py` |
| What the backend freeze permits | `src/pontonier/backend/__init__.py` |
| Norms and prohibitions | [AGENTS.md](AGENTS.md) |
| Setup, gate, commit format | this file |
| Release procedure | [docs/releasing.md](docs/releasing.md) |
| Repo settings and their rationale | [docs/github-config.md](docs/github-config.md) |
