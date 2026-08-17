# GitHub configuration

The rules in [AGENTS.md](../AGENTS.md) are advisory — an agent can ignore them, and a
prompt-injected one will. This page is the enforced half: what is configured on the
repository itself, and how to reapply it.

Everything here needs **admin scope**. The local agent identity
(`briandconnelly-agent[bot]`) does not have it and gets `403` on these endpoints,
which is intentional: an identity that can edit the ruleset is not bound by it.
Run these commands as the maintainer.

## Status

Applied and verified on 2026-08-17. The payloads in `docs/rulesets/` are what was
accepted; re-POST them to rebuild the configuration from scratch.

| Control | State |
| --- | --- |
| Branch ruleset on `main` | **active** — ruleset `protect main` |
| Tag ruleset on `v*` | **active** — ruleset `protect release tags` |
| `pypi` environment approval | **active** — requires review from `briandconnelly` |
| `pypi` deployment branch policy | **active** — `main` (branch) and `v*.*.*` (tag) only |
| Prevent self-review on `pypi` | **off**, deliberately — see §3 |
| Delete branch on merge | **on** |
| Auto-merge | **off**, deliberately — it would let a PR land with no human in the loop |
| Classic branch protection | unknown — the endpoint returns 403 to a non-admin token |
| Agent App `workflows` permission | **not granted** — verified below |

Verify the rules actually in force on the default branch — not merely that a ruleset
exists — with:

```sh
gh api repos/briandconnelly/pontonier/rules/branches/main --jq '[.[] | .type]'
# ["deletion","non_fast_forward","pull_request","required_status_checks"]
```

The last row is confirmed, not assumed: pushing a branch that edited
`.github/workflows/ci.yml` as the agent identity was rejected by GitHub with
*"refusing to allow a GitHub App to create or update workflow … without `workflows`
permission"*. Keep it that way. It means changes to CI — the thing that decides what
"green" means — always pass through the maintainer's own credentials.

## The solo-maintainer constraint

This is a single-maintainer repository, and that shapes every choice below. GitHub
does not let an author approve their own pull request, so any rule that *requires* an
approving review — including required code-owner review — locks the only human out of
merging their own work. The ruleset therefore requires a pull request and a green
`gate`, but **zero approvals**.

What that does and does not buy:

- Enforced: no direct push to `main`, no force-push, no deletion, and no merge until
  `gate` passes.
- Not enforced: that a human, rather than the agent, presses Merge. That one stays
  advisory — [AGENTS.md](../AGENTS.md#off-limits-without-explicit-human-instruction)
  forbids it, and CODEOWNERS auto-requests your review on every PR so you see it.

When a second maintainer or reviewer exists, raise
`required_approving_review_count` to 1 and set `require_code_owner_review: true`.
Until then, do not — it would be a lockout, not a control.

## 1. Protect `main`

Requires the `gate` check from `.github/workflows/ci.yml` — one stable context that
aggregates the whole test matrix, so adding a Python version cannot silently drop
coverage from the rule.

```sh
gh api repos/briandconnelly/pontonier/rulesets \
  --method POST --input docs/rulesets/main.json
```

`bypass_actors` is empty. Never add an automation identity: the agent's whole
constraint is this rule. If you later want a personal escape hatch for direct pushes,
add yourself through Settings → Rules → the ruleset → Bypass list, which only offers
actors GitHub considers eligible.

## 2. Protect `v*` tags

A pushed tag no longer triggers a publish (see §5), so this ruleset is about integrity
rather than triggering: it makes existing release tags immutable. They cannot be moved,
deleted, or force-updated, so a published version can never come to point at different
code.

```sh
gh api repos/briandconnelly/pontonier/rulesets \
  --method POST --input docs/rulesets/tags.json
```

**Tag *creation* is deliberately not restricted here.** Restricting it would also stop
the release workflow's `create-tag` job, which pushes the tag with `GITHUB_TOKEN`
before the `pypi` approval gate — so the rule would need a bypass actor for GitHub
Actions, and whether the built-in Actions app is an eligible bypass actor for a
repository ruleset is unverified. It matters less than it did: since a tag push no
longer triggers `publish.yml` (§5), a stray tag is now inert rather than a publish
trigger.

## 3. Pin the pypi environment to release refs

The environment's human approval is the last thing between a workflow run and PyPI.
Without a branch policy any ref could reach it, so it is pinned to release refs — the
guard then holds even if the workflow file is edited in a PR:

```sh
gh api repos/briandconnelly/pontonier/environments/pypi \
  --method PUT --input - <<'JSON'
{
  "deployment_branch_policy": {
    "protected_branches": false,
    "custom_branch_policies": true
  }
}
JSON

gh api repos/briandconnelly/pontonier/environments/pypi/deployment-branch-policies \
  --method POST -f name='main' -f type='branch'

gh api repos/briandconnelly/pontonier/environments/pypi/deployment-branch-policies \
  --method POST -f name='v*.*.*' -f type='tag'
```

The JSON body matters: those two fields are booleans, and `gh api -f/--raw-field`
would send them as the strings `"false"` and `"true"`, which the API rejects.

**Leave "Prevent self-review" off** while you are the only reviewer — it stops the
person who dispatched the workflow from approving the deployment, which on a
one-person repository means nothing can ever be published. Turn it on in the same
change that adds a second eligible reviewer.

## 4. Housekeeping

```sh
gh repo edit briandconnelly/pontonier --delete-branch-on-merge
```

## 5. Audit the agent App's permissions

Dispatching the Publish workflow is the only path to a release, so the agent App must
not be able to dispatch workflows.

**Read the grants in the UI:** <https://github.com/settings/installations> → the
agent App → *Permissions*. This is the authoritative view and needs no token.

Verified 2026-08-17:

| Grant | Level |
| --- | --- |
| actions, checks, commit statuses, metadata | read |
| code (contents), issues, pull requests | read and write |
| workflows, administration, environments | **not granted** |

That set is the intended one. `actions: read` rather than write is what matters most:
the agent can watch CI but cannot dispatch a workflow, which closes the
`workflow_dispatch` route to a release. No `administration` means it cannot edit the
rulesets that constrain it, and no `workflows` means it cannot edit CI — both verified
by `403`s and a rejected push rather than assumed.

`contents: write` is not separable from tag creation, so the agent can still create a
`v*.*.*` tag. `publish.yml` no longer triggers on a pushed tag, which makes that tag
inert: releasing requires `workflow_dispatch`, and dispatching requires
`actions: write`, which the agent does not have. **Do not add the tag-push trigger
back without also restricting tag creation.**

Two human gates remain behind that, unchanged: the `pypi` environment approval, and
the branch policy limiting which refs can reach it. An approval request you did not
initiate is a signal to investigate, not to click.

Two API routes look like they would answer this and do not:

| Endpoint | Why it fails |
| --- | --- |
| `GET /user/installations` | Needs a user-to-server token from an OAuth flow. A `gh` CLI token is not one; it returns `403 You must authenticate with an access token authorized to a GitHub App`. |
| `GET /repos/{owner}/{repo}/installation` | Needs a GitHub App JWT, not a user token. |

The scriptable route is a JWT signed with the App's private key, then
`GET /app/installations/{installation_id}`, whose response carries `permissions`.
Mint the JWT the same way `bot-token` does. That reads the App private key, so run it
as yourself rather than from an agent session.

## What is deliberately not configured

- **Required signed commits.** Attribution already comes from the distinct bot App
  identity; signing is worth adding but is not load-bearing here.
- **Required approvals.** See the solo-maintainer constraint above.
