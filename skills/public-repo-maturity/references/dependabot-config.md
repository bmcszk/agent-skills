# Dependabot config (dependabot.yml template)

`.github/dependabot.yml`. One `updates:` entry per ecosystem/manifest pair.

```yaml
version: 2
updates:
  - package-ecosystem: gomod
    directory: /
    schedule:
      interval: weekly
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

Common ecosystems: `gomod`, `github-actions`, `npm`, `pip`, `docker`,
`maven`, `gradle`, `cargo`, `composer`, `nuget`, `terraform`.

## Grouping (update-noise control)

```yaml
  - package-ecosystem: gomod
    directory: /
    schedule:
      interval: weekly
    groups:
      minor-and-patch:
        update-types:
          - minor
          - patch
```

## When NOT to group gomod

Grouped bumps hide directive-breaking upgrades: one transitive dep raising
the `go` directive rides in a PR titled "minor-and-patch" and a green matrix
proves nothing when GOTOOLCHAIN=auto silently downloads the newer toolchain
(see SKILL.md pitfalls). For compiled/production-critical ecosystems prefer
ungrouped (or group patch-only) so each PR is bisectable. Grouping is fine
for `github-actions` - actions rarely change toolchain floors, and
Dependabot keeps the peeled-SHA pins fresh, which Pinned-Dependencies
scores.

## Extras

- `open-pull-requests-limit: 5` (default 5) - raise only if you actually
  merge weekly.
- `reviewers:` / `assignees:` accept teams as `org/team-slug`.
- `registries:` block for private registries; credentials live in repo
  secrets, never inline.

## Monorepo action groups (the codeql-action pattern)

An action monorepo publishing multiple sub-actions
(`github/codeql-action/init|autobuild|analyze|upload-sarif`) gets ONE
Dependabot PR per sub-action ref. When the workflow's steps must run at a
UNIFORM version (CodeQL writes config at the init version and rejects any
step running a different one: "Loaded a configuration file for version X,
but running version Y"), no individual PR can EVER pass CI while the others
are pending - mixed refs are fatal on any merge order.

Recipe when that happens:
1. Confirm the failure signature is version-skew (grep `--log-failed` for
   "Loaded a configuration file"), not a real code break.
2. Close the whole split group with a comment pointing at a single atomic
   bump PR that sets ALL refs to the new peeled SHA in one commit
   (`chore(deps): bump <action> all refs to vX.Y.Z (atomic)`). All-newer or
   all-older; never a mix. Merging a partial prefix leaves MASTER broken
   (mixed refs), so the atomic PR also repairs the window opened by any
   already-merged member.
3. Verify uniformity after merge: `grep -c <new-sha> workflow.yml` == ref
   count, `grep -c <old-sha>` == 0, then confirm master's run goes green.

## Agent-token scope wall on workflow-file PRs

An OAuth token without the `workflow` scope CANNOT: edit workflow files on a
branch, `gh pr update-branch` a PR that touches `.github/workflows`, or
merge such a PR (even with `--admin` - "requires the workflow scope").
CAN: post `@dependabot rebase` / `@dependabot recreate` comments (Dependabot
itself pushes the rebased branch), comment, close, create its own branches.
So for workflow PRs: drive branches via `@dependabot` commands, ship
replacement bumps as your own PR from a fresh branch, and hand the final
merge click to the user.

