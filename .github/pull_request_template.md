## What changed

<!-- One or two sentences. Link the issue if there is one. -->

## Why

<!-- The problem this solves. For a behavior change, what a consumer would notice. -->

## Checklist

- [ ] `uv run scripts/check.sh` passes locally
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`, if behavior changed
- [ ] Docs describing the changed behavior updated in this PR
- [ ] No new runtime dependency (or: it is justified in the changelog entry)
- [ ] `pontonier.backend` changes respect the freeze — no new *required* Protocol
      member or `BackendContract` field
