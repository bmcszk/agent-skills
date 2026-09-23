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
for `github-actions` — actions rarely change toolchain floors, and
Dependabot keeps the peeled-SHA pins fresh, which Pinned-Dependencies
scores.

## Extras

- `open-pull-requests-limit: 5` (default 5) — raise only if you actually
  merge weekly.
- `reviewers:` / `assignees:` accept teams as `org/team-slug`.
- `registries:` block for private registries; credentials live in repo
  secrets, never inline.
