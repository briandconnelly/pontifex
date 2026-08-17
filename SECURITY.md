# Security

## Reporting a vulnerability

Report privately through
[GitHub Security Advisories](https://github.com/briandconnelly/pontonier/security/advisories/new).
Do not open a public issue for a vulnerability.

Expect an acknowledgement within a week. This is a personal project, not a funded one
— there is no formal SLA beyond that, and no bug bounty.

## What is in scope

pontonier runs subprocesses, manages throwaway git worktrees, redacts diffs, and
stores job records on disk on behalf of agent-bridge MCP servers. The parts most
worth your attention:

- **`core.redaction`** — secret redaction is documented as best-effort. A pattern it
  misses is a bug worth reporting; the fact that it is not a guarantee is not.
- **`core.jobs`** — job ids are confined to the minted 32-hex shape precisely because
  they become path components. Any way to escape the store root is in scope.
- **`core.gitproc` / `core.worktree`** — argument injection into git, or a worktree
  that outlives its cleanup, are in scope.
- **`core.runtime` / `core.streamcap`** — unbounded output or a leaked child process.

## Out of scope

- The behavior of the agent CLIs the bridges invoke (Codex, Claude Code, Kimi).
- Anything requiring an attacker who already has local code execution as the user.
- The consuming bridges themselves — report those in their own repositories.
