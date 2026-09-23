# GitHub Actions badges + badge family (README wiring)

How a mature public repo's README badge row is assembled and what feeds
each badge. All URLs verified against a live repo; `<owner>/<repo>` and
`<default>` = default branch name (`master` or `main`).

## The badge family (paste-ready)

```markdown
[![Tests](https://github.com/<owner>/<repo>/actions/workflows/<test-workflow>.yml/badge.svg?branch=<default>)](https://github.com/<owner>/<repo>/actions/workflows/<test-workflow>.yml)
[![Security](https://github.com/<owner>/<repo>/actions/workflows/<security-workflow>.yml/badge.svg?branch=<default>)](https://github.com/<owner>/<repo>/actions/workflows/<security-workflow>.yml)
[![coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/<owner>/<repo>/gh-pages/badges/coverage.json&cacheSeconds=3600)](<link to workflow or docs>)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/<owner>/<repo>/badge)](https://scorecard.dev/viewer/?uri=github.com/<owner>/<repo>)
[![Go Reference](https://pkg.go.dev/badge/<module-path>.svg)](https://pkg.go.dev/<module-path>)
[![License](https://img.shields.io/github/license/<owner>/<repo>)](./LICENSE)
```

Badge types and their feeders:

| Badge | Feeder | Notes |
|---|---|---|
| workflow status | `actions/workflows/<file>.yml/badge.svg?branch=<default>` | works for ANY workflow file; `?branch=` pins the default branch or the badge shows last run on any ref |
| coverage | shields `endpoint` + JSON on `gh-pages` | see zero-dependency recipe below; no codecov/service account |
| scorecard | `api.scorecard.dev/.../badge` | resolves only after a `publish_results: true` run (`references/scorecard-workflow.md`); viewer link = `https://scorecard.dev/viewer/?uri=github.com/<owner>/<repo>` |
| pkg.go.dev | pkg.go.dev auto-badge | appears once the module is publicly fetchable; `go install` from a clean cache to verify |
| license | shields `github/license` | requires LICENSE file at root |
| CII badge | `bestpractices.dev/projects/<id>/badge` | `<id>` from the project URL after registration (`references/user-side-checklist.md`) |

## Zero-dependency coverage badge (gh-pages + shields endpoint)

Codecov-style services need an account and leak coverage history to a
third party. This recipe keeps everything in the repo. In the test
workflow:

1. Job needs `permissions: {contents: write}` (to push gh-pages).
2. Run tests with a coverage profile (single matrix leg only, default
   branch only, so concurrent matrix jobs don't race the push):

```yaml
    - name: Publish coverage badge (newest Go + default branch only)
      if: matrix.go-version == '1.24' && github.ref == 'refs/heads/<default>'
      run: |
        PCT=$(go tool cover -func=coverage.out | awk '/total/ {gsub("%",""); print $3}')
        COLOR=brightgreen; awk -v p="$PCT" 'BEGIN{exit !(p<80)}' && COLOR=green
        awk -v p="$PCT" 'BEGIN{exit !(p<60)}' && COLOR=yellow
        mkdir -p /tmp/badges
        printf '{"schemaVersion":1,"label":"coverage","message":"%s%%","color":"%s"}' "$PCT" "$COLOR" > /tmp/badges/coverage.json
        git config user.name "github-actions[bot]"
        git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
        git fetch origin gh-pages --depth=1 2>/dev/null || true
        if git rev-parse --verify origin/gh-pages >/dev/null 2>&1; then
          git checkout -B gh-pages origin/gh-pages
        else
          git checkout --orphan gh-pages
          git rm -rf . >/dev/null 2>&1 || true
        fi
        mkdir -p badges
        cp /tmp/badges/coverage.json badges/coverage.json
        git add badges/coverage.json
        git commit -m "chore(badges): coverage $PCT%" --allow-empty
        git push origin gh-pages
```

3. README embeds the shields endpoint against the raw file (with a short
   `cacheSeconds` so updates show within the hour):

```markdown
[![coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/<owner>/<repo>/gh-pages/badges/coverage.json&cacheSeconds=3600)](<workflow URL>)
```

### Gotchas

- `gh-pages` must hold ONLY generated artifacts — an orphan branch, not a
  copy of the source tree; anything else ships repo files to the web.
- `--allow-empty` on the badge commit: repeated coverage can be identical;
  without the flag the push no-ops and the next run fails on `git commit`.
- Single-leg `if:` guard is load-bearing: two matrix legs pushing gh-pages
  concurrently = one wins, one fails the job (a red X on an otherwise
  green PR).
- Concurrency: if other workflows also push gh-pages (e.g. docs), add
  `concurrency: {group: gh-pages, cancel-in-progress: false}` to serialize.
- Threshold colors are a policy choice; keep the awk one-liners, don't add
  a threshold config file for two numbers.
