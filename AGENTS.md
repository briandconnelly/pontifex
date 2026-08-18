# AGENTS.md

Repo-wide norms for anyone working in pontonier, human or agent. This file is the
canonical instruction file; `CLAUDE.md` points here. Keep it short — procedures live
in linked documents, not inline.

## Verify

Run the full gate before you claim work is done. It is the same gate CI runs:

```sh
./scripts/check.sh
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

## Bridge intake

What this library accepts from a bridge, and what stays in the bridge.
[README.md](README.md) lists the three bridges. The downstream half of this decision is
`codex-in-claude`'s
[Package boundary](https://github.com/briandconnelly/codex-in-claude/blob/main/AGENTS.md#package-boundary).
Read it there. Do not copy it here.

- **Accept only shared mechanisms.** A mechanism is accepted when it is independent of one
  bridge's CLI, harness, and MCP surface, and when it extends an abstraction this library
  already exposes or has a confirmed need in more than one bridge. The absence of a
  bridge's name in the code is not evidence that the mechanism is shared. A second caller
  that does not exist yet is not a confirmed need.
- **Bridge policy stays in the bridge.** CLI assumptions, tool and result semantics, and
  knobs a bridge pins on purpose (`codex-in-claude`'s `WORKTREE_CONFIG`) stay downstream.
  Policy built on a type from here is still bridge policy.
- **A mixed change lands in two repositories.** A shared mechanism plus bridge policy is
  the usual case, not an exception. Do not accept the policy half to keep the change in one
  pull request.
- **A fix a bridge waits for needs a release.** Bridges pin an exact version, and a bridge
  cannot merge a pin to an unpublished version. A merge to `main` here does not ship. Land
  the fix, release it, and then the bridge bumps its pin. See
  [docs/releasing.md](docs/releasing.md).
- **Say when a value bridges expose changes.** A bridge can re-export a value from here on
  its agent-visible surface — `codex-in-claude` exposes `DEFAULT_POLL_AFTER_MS` as
  `JOB_POLL_AFTER_MS`. This repository does not judge a bridge's fingerprint, breaking
  status, or version. Record the change in [CHANGELOG.md](CHANGELOG.md) so each bridge can
  make that call.
- **Test behavior where it is owned.** Test the implementation and its full input domain
  here. The bridge tests the adapter, the mapping, and the agent-visible regression.

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
| Does a change belong here or in a bridge? | [Bridge intake](#bridge-intake) |
| Why is the code shaped this way? | The package `__init__.py` docstrings |
| What changed and why? | [CHANGELOG.md](CHANGELOG.md) — history, not current policy |

`CHANGELOG.md` records decisions as they were made. It is not authoritative for how
things work now; if a rule matters today it belongs in this file or in a doc linked
from it.
