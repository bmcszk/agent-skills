# Scorecard workflow (scorecard.yml template)

Full `.github/workflows/scorecard.yml`. Pin both actions to peeled commit
SHAs (resolve the current tag with `git ls-remote
https://github.com/<owner>/<repo> refs/tags/vX.Y.Z^{}` — `^{}` gives the
peeled commit, not the annotated tag object).

```yaml
name: Scorecard
on:
  branch_protection_rule:
  schedule:
    - cron: '40 5 * * 2'
  push:
    branches: [master]
  workflow_dispatch:

permissions: {}

jobs:
  analysis:
    name: Scorecard analysis
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      id-token: write
      contents: read
      actions: read
    steps:
      - name: Checkout
        uses: actions/checkout@<peeled-sha> # v4.x
        with:
          persist-credentials: false
      - name: Run analysis
        uses: ossf/scorecard-action@<peeled-sha> # v2.x
        with:
          results_file: results.sarif
          results_format: sarif
          publish_results: true
      - name: Upload artifact
        uses: actions/upload-artifact@<peeled-sha> # v4.x
        with:
          name: SARIF-file
          path: results.sarif
          retention-days: 5
      - name: Upload to code scanning
        uses: github/codeql-action/upload-sarif@<peeled-sha> # v3.x
        with:
          sarif_file: results.sarif
```

## Non-obvious requirements

- `publish_results: true` is what makes the public API
  (`api.scorecard.dev/projects/github.com/<owner>/<repo>`) update. Without
  it the run is local-only and the README badge never moves.
- Publishing requires `id-token: write` (keyless OIDC). Public repos have
  this by default; private repos cannot publish at all.
- `persist-credentials: false` on checkout — the Scorecard tool itself
  flags leaked tokens and Dangerous-Workflow patterns; do not ship the
  workflow with the default credential persistence.
- Top-level `permissions: {}` + per-job grants is the Token-Permissions
  check's preferred shape; a blanket `contents: write` costs points.
- Weekly cron: Scorecard's Maintained and date-sensitive checks read the
  freshest published run; a one-shot workflow goes stale.

## README badge

```markdown
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/<owner>/<repo>/badge)](https://api.scorecard.dev/projects/github.com/<owner>/<repo>)
```

Badge renders `unknown` until the first published run completes — fix the
workflow, not the badge URL.
