# Changelog

All notable changes to this project will be documented in this file. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### 0.4.0 (redaction strengthening — key-block handling flows into core)

- `core.redaction` now redacts multi-line private-key blocks (PEM/PKCS8/OpenSSH/
  PGP) STATEFULLY — ported from the claude-in-codex bridge's local redactor,
  closing the pre-unification gap recorded under 0.3.0. The BEGIN/END markers
  stay visible so a reviewer sees what was dropped; every body line between them
  is replaced 1:1 with `[redacted: secret value]` (hunk line counts survive, so
  a redacted patch still applies); an UNTERMINATED block fails closed, redacted
  to end of input; a block never bleeds across `diff --git` headers or
  hunk/metadata boundaries; and the inline patterns scan the key pass's output,
  so a token sharing the END marker's physical line is still caught. Applies to
  `redact`/`DiffRedactor` (key masks flow through the same staged
  `masked_paths`/`inline_masks` accounting, including withhold dominance) and to
  `redact_text`/`redact_tree`/`exc_summary`.
- REMOVED the `-----BEGIN [A-Z ]*PRIVATE KEY-----` entry from
  `SECRET_VALUE_PATTERNS`. It masked the BEGIN marker itself while shipping the
  entire base64 body — a disclosure marker claiming coverage it did not have —
  and its missing trailing alternation never matched PGP's "PRIVATE KEY BLOCK"
  suffix at all. The stateful pass owns key material now; output for
  key-bearing input changes accordingly (markers visible, body dropped).

### 0.3.0 (protocol feedback from the three real adapters — still PROVISIONAL)

- `RunOutcome.events` is now an OPAQUE raw payload string instead of parsed
  event dicts. The Codex adapter showed that typed dicts forced eager parsing
  upstream of the tolerance boundary — real normalize layers must parse
  tolerantly so a malformed line degrades instead of raising. Its docs also now
  state that a backend may use neither the events nor the artifacts channel
  (the Claude adapter reads everything from the stdout envelope).
- `BackendContract.effort_validation` (defaulted, non-breaking) declares how
  pre-spend effort validation works: `enumerated` (Claude),
  `token_floor_plus_catalog` (Kimi — universal token floor, catalog-relative
  refinement, failing OPEN when the catalog cannot answer), or `shape_only`
  (Codex — upstream rejects bad values loudly; only argv-hostile shapes are
  refused locally).
- Deferred to the freeze window, recorded from adapter findings: a shared seam
  for the prompt-append schema-instruction text (currently duplicated in the
  Kimi bridge under a byte-parity test), and classification's ambient
  extra-args context.
- `JobStore.start` (and `start_idempotent` via passthrough) accepts
  `stdin_text`: streamed to the worker over a pipe by a daemon thread, never
  persisted — the transport for bridges whose prompts must stay off disk and
  off argv (the claude bridge's design). Default `None` keeps the prior
  DEVNULL behavior byte-identical.
- Known gap, discovered during the claude-in-codex context comparison:
  `core.redaction` has NO multi-line PEM/OpenSSH/PGP key-block handling — a
  private key pasted into a tracked file's diff (or returned in prose) is
  scrubbed only if the inline value patterns happen to match. claude-in-codex's
  local redactor handles these blocks statefully (failing closed on an
  unterminated block); that handling must flow into `core.redaction` BEFORE any
  bridge unifies onto the shared engine, or unification would weaken redaction.

### 0.2.0 (milestone M1 — conventions + provisional protocol)

- `pontifex.conventions.envelope`: shared error taxonomy — universal codes
  (the verified intersection across the three bridges), backend-prefixed code
  minting, feature-gated codes (`transfer`, `model_validation`,
  `empty_response_detection`), and per-code `RepairRule` tables parameterized
  by a `BackendErrorVocabulary`. Wire serialization deliberately stays
  consumer-side.
- `pontifex.conventions.prompts`: the shared framing/builders, with the host
  harness name as a parameter; `framings("Claude Code")` reproduces the
  source bridges' prose byte-for-byte (pinned by tests).
- `pontifex.conventions.annotations`: tool-annotation builders parameterized
  by declared effects (`AnnotationEffects`) instead of universal constants —
  the bridges' differing values are deliberate positions, now explicit.
- `pontifex.conventions.preflight`: `HelpProbe` (instance-cached `--help`
  feature detection, fail-open) generalizing the per-repo module.
- `pontifex.conventions.fingerprint`: the surface-digest / fingerprint-bump
  invariant as reusable, framework-agnostic mechanics.
- `pontifex.backend` (**PROVISIONAL**, `CONTRACT_API_VERSION = 0`):
  `BackendContract` (static facts: flag classes, failure-signature tables,
  field-scoped model-catalog authority, typed extra-args policy, isolation
  policy, limits), the `AgentBackend` protocol as a staged lifecycle
  (`validate_request` → `prepare` → `finalize`/`classify_failure`), shared
  `RunRequest`/`PreparedRun`/`RunOutcome`/`ExecResult` types, and a shared
  failure classifier with fixed precedence and a backend hook.
- `pontifex.testing`: importable, framework-agnostic test kit —
  surface-honesty phrase scanning, adapter/contract conformance checks
  (including the mandatory pre-spend effort-validation invariant), and
  sync/async pair parity. No pytest dependency.
- Three fake adapters (Codex-like, Kimi-like, Claude-like) validate that the
  provisional protocol expresses all three real invocation shapes.
- Deviation from plan, documented: no `pydantic` dependency was added — the
  backend/conventions layers are plain dataclasses, so the wheel still
  depends only on `anyio`. The planned `testing` extra is unnecessary for the
  same reason (the kit imports no test framework).

### 0.1.0 (milestone M0 — core extraction)

- `pontifex.core`: the CLI-agnostic machinery extracted from moonbridge's
  `_core` (jobs, worktree, gitdiff, redaction, runtime, gitproc, streamcap,
  idempotency, workspace, jsoncache), carrying the redaction
  trailing-newline fix and the orphan-process sweep.
- `WorktreeConfig`: worktree prefix, baseline-commit identity, and extra
  exclude pathspecs are per-consumer fields with behavioral tests.
- One-way dependency rule (`core` imports nothing from the rest) enforced by
  import-linter in CI.
