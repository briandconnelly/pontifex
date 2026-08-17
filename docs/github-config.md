# GitHub configuration

The rules in [AGENTS.md](../AGENTS.md) are advisory — an agent can ignore them, and a
prompt-injected one will. This page is the enforced half: what is configured on the
repository itself, and how to reapply it.

Everything here needs **admin scope**. The local agent identity
(`briandconnelly-agent[bot]`) does not have it and gets `403` on these endpoints,
which is intentional: an identity that can edit the ruleset is not bound by it.
Run these commands as the maintainer.

## Status

| Control | State as of 2026-08-16 |
| --- | --- |
| Branch ruleset on `main` | **absent** — `gh api repos/briandconnelly/pontonier/rulesets` returns `[]` |
| Tag ruleset on `v*` | **absent** — same |
| `pypi` environment approval | present — requires review from `briandconnelly` |
| `pypi` deployment branch policy | **absent** — `deployment_branch_policy: null`, any ref can deploy |
| Delete branch on merge | **off** |
| Classic branch protection | unknown — the endpoint returns 403 to a non-admin token |

Re-check the first two at any time with:

```sh
gh api repos/briandconnelly/pontonier/rulesets --jq '.[] | {name, target, enforcement}'
```

## 1. Protect `main`

Requires the `gate` check from `.github/workflows/ci.yml` — one stable context that
aggregates the whole test matrix, so adding a Python version cannot silently drop
coverage from the rule.

```sh
gh api repos/briandconnelly/pontonier/rulesets \
  --method POST --input docs/rulesets/main.json
```

`bypass_actors` is empty in that file. On a solo repository that means *you* also
cannot push straight to `main` — you merge your own PRs instead, which is the
intended trade. If you want a personal escape hatch, add yourself in
Settings → Rules → the ruleset → Bypass list. Never add an automation identity: the
agent's whole constraint is this rule.

## 2. Protect `v*` tags

The publish workflow triggers on a pushed `v*.*.*` tag, so tag creation is a publish
trigger and belongs behind the same kind of gate as `main`.

```sh
gh api repos/briandconnelly/pontonier/rulesets \
  --method POST --input docs/rulesets/tags.json
```

The ruleset restricts **creation** as well as update and deletion — a tag nobody can
create is a publish nobody can trigger. That leaves one deliberate hole: the release
workflow's `create-tag` job pushes the tag itself, and it runs *before* the `pypi`
environment approval. So the GitHub Actions app (`actor_id: 15368`, verified via
`gh api apps/github-actions`) is the single bypass actor.

That is a real trade-off, stated plainly: anyone who can dispatch the Publish
workflow can still cause a tag. It is narrower than it looks — dispatching needs
`actions: write`, which the agent App should not hold (see the audit item below) —
and the environment approval still gates the upload itself. Verify with:

```sh
gh api repos/briandconnelly/pontonier/installation --jq '.permissions'   # as maintainer
```

If that shows `actions: write` for the agent installation, remove it.

## 3. Pin the pypi environment to release refs

Today the environment's human approval is the only thing between a workflow run and
PyPI, and any ref can reach it. Restrict it so the guard holds even if the workflow
file is edited in a PR:

```sh
gh api repos/briandconnelly/pontonier/environments/pypi \
  --method PUT \
  --raw-field 'deployment_branch_policy[protected_branches]=false' \
  --raw-field 'deployment_branch_policy[custom_branch_policies]=true'

gh api repos/briandconnelly/pontonier/environments/pypi/deployment-branch-policies \
  --method POST -f name='main' -f type='branch'

gh api repos/briandconnelly/pontonier/environments/pypi/deployment-branch-policies \
  --method POST -f name='v*.*.*' -f type='tag'
```

Also turn on **Prevent self-review** for the environment in
Settings → Environments → pypi, so the approval is a real second pair of eyes when
someone else is added as a reviewer later.

## 4. Housekeeping

```sh
gh repo edit briandconnelly/pontonier --delete-branch-on-merge
```

## What is deliberately not configured

- **Required signed commits.** Attribution already comes from the distinct bot App
  identity; signing is worth adding but is not load-bearing here.
- **Required reviewers on the branch ruleset beyond CODEOWNERS.** A solo repository
  with a required code-owner review already routes every agent PR to a human.
