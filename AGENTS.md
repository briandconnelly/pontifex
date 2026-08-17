# AGENTS.md

Repo-wide norms for anyone working in pontonier, human or agent. This file is the
canonical instruction file; `CLAUDE.md` points here. Keep it short — procedures live
in linked documents, not inline.

## Verify

Run the full gate before you claim work is done. It is the same gate CI runs:

```sh
uv run scripts/check.sh
```

Do not report success from a subset of it. Individual steps are listed in
[CONTRIBUTING.md](CONTRIBUTING.md#the-gate) for when you need to iterate on one.

## Rules

- **`pontonier.core` never imports from the rest of the package.** import-linter
  enforces this in the gate. See `src/pontonier/core/__init__.py` for why.
- **`pontonier.backend` is FROZEN** at `CONTRACT_API_VERSION = 1`. Adding a required
  Protocol member or a required `BackendContract` field is a breaking change, not an
  additive one. New behavior lands as an optional capability protocol or a defaulted
  field. `src/pontonier/backend/__init__.py` is the authority on what the freeze
  permits; do not restate the rule elsewhere.
- **The package depends only on `anyio`.** A new runtime dependency changes the
  contract for all three consuming bridges — raise it before adding one.
- **Coverage floor is 95%**, enforced by the gate. Do not lower `fail_under`.
- **Commit messages are Conventional Commits.** Format and allowed scopes:
  [CONTRIBUTING.md](CONTRIBUTING.md#commit-messages). A commit-msg hook checks this;
  install it with `prek install --hook-type commit-msg`.
- **Branch names** are `type/short-description`, matching the commit type
  (`feat/…`, `fix/…`, `chore/…`).
- **Never restate a rule that already has a home.** Link to it. Three copies of the
  freeze rule is how the copy in the tests went stale.

## Off limits without explicit human instruction

- **Do not release.** Do not create or push `v*` tags, dispatch
  `.github/workflows/publish.yml`, create GitHub Releases, or publish to PyPI.
  Release prep an agent *may* do, when asked, is in [docs/releasing.md](docs/releasing.md).
- **Do not merge your own pull request**, and do not approve it. Green checks are a
  gate outcome, not permission to merge. Merge authority is the maintainer's unless
  they say otherwise in the session.
- **Do not push to `main`.** Work on a branch and open a PR.
- **Do not edit `.github/workflows/**`, `CODEOWNERS`, or this file** as a side effect
  of another task. They are code-owned; change them as their own reviewed PR.
- **Do not rewrite published history** or force-push a branch someone else is reviewing.

## Where things are

| Question | Read |
| --- | --- |
| What does this library do, what is in each module? | [README.md](README.md) |
| How do I set up, run the gate, format a commit? | [CONTRIBUTING.md](CONTRIBUTING.md) |
| How is a release cut? | [docs/releasing.md](docs/releasing.md) |
| What repo settings enforce all this? | [docs/github-config.md](docs/github-config.md) |
| Why is the code shaped this way? | The package `__init__.py` docstrings |
| What changed and why? | [CHANGELOG.md](CHANGELOG.md) — history, not current policy |

`CHANGELOG.md` records decisions as they were made. It is not authoritative for how
things work now; if a rule matters today it belongs in this file or in a doc linked
from it.
