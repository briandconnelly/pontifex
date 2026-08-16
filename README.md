# pontifex

Pontifex is the shared core library for agent-bridge MCP servers. An
agent bridge lets one agent harness call an agent that runs on a
different model. Three bridges use this library:

- [codex-in-claude](https://github.com/briandconnelly/codex-in-claude) — Claude Code → Codex CLI
- [moonbridge](https://github.com/briandconnelly/moonbridge) — Claude Code or Codex → Kimi CLI
- [claude-in-codex](https://github.com/briandconnelly/claude-in-codex) — Codex → Claude Code CLI

The name is Latin for "bridge-builder": pontifex is not itself a
bridge — it is what the bridges are built from.

> **Note:** The unrelated PyPI package `agentbridge` is a different
> project. This library is `pontifex`.

## What is in the box

`pontifex.core` — backend-agnostic machinery, extracted from the
bridges' `_core` packages:

| Module | Purpose |
| --- | --- |
| `jobs` | Disk-backed, daemonless async job store |
| `worktree` | Throwaway git worktrees for delegated work |
| `gitdiff` | Bounded, redacted git diff gathering |
| `redaction` | Best-effort secret redaction for diffs and prose |
| `runtime` | Subprocess execution with bounded streams and cleanup |
| `gitproc` | Hardened git subprocess helpers |
| `streamcap` | Bounded stream capture |
| `idempotency` | On-disk idempotency-key index |
| `workspace` | MCP-root workspace resolution |
| `jsoncache` | Small JSON file cache |

**Rule:** `pontifex.core` never imports from the rest of the package.
CI enforces this with import-linter.

`pontifex.conventions` — the shared vocabulary bridges are built from:
error taxonomy + repair rules (`envelope`), host-parameterized prompt
framing (`prompts`), effect-parameterized tool annotations
(`annotations`), CLI `--help` feature detection (`preflight`), and the
surface-fingerprint invariant (`fingerprint`). Wire serialization stays
in each bridge.

`pontifex.backend` — **provisional** (`CONTRACT_API_VERSION = 0`): the
`BackendContract` static-facts dataclass, the `AgentBackend` staged run
lifecycle (`validate_request` → `prepare` → `finalize`/`classify_failure`),
and a shared failure classifier with fixed precedence. It freezes only
after all three real adapters pass their conformance and golden fixtures.

`pontifex.testing` — importable, framework-agnostic test kit: surface
honesty (forbidden-phrase scanning against the built wire), adapter and
contract conformance, and sync/async tool-pair parity. Checks return
violation lists; wire them into any harness.

## Development

This project uses [uv](https://docs.astral.sh/uv/):

```sh
uv sync
uv run pytest
uv run ruff check
uv run lint-imports
```
