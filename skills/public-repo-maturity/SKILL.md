---
name: public-repo-maturity
description: Use when raising a public repo's Scorecard/CII maturity.
---

# Public repo maturity (OpenSSF Scorecard / CII)

Scope: making a public repo adoptable by security-conscious users — raising
OpenSSF Scorecard, earning the CII Best Practices badge, shipping signed
releases. Language-agnostic; Go examples where concrete.

## Procedure

1. **Baseline first, live.** Fetch the current scorecard with per-check
   scores via the public API
   (`https://api.scorecard.dev/projects/github.com/<owner>/<repo>`) — never
   assert a check's score from memory; the report lags merges by hours and
   only a live read tells you what actually moved.
2. **Split every remaining delta into agent-side vs user-side before
   proposing.** Agent-side (shippable as PRs): fuzz targets, release
   workflow with signing, pinned actions, SBOM. User-side (Settings clicks
   or account signups the agent cannot do): branch protection, secret
   scanning/push protection, Dependabot alerts, CII registration (account +
   self-certification questionnaire on bestpractices.dev). Present the
   split; do the agent side, give exact click-paths for the user side.
3. **Raise Scorecard by the checks doc, not vibes.** Anchor:
   `ossf/scorecard` repo `docs/checks.md` (pin the commit SHA you read).
   Each check names exactly what it detects (e.g. Fuzzing = in-repo
   language-native fuzz functions; CII-Best-Practices = badge status via
   bestpractices.dev API: gold 10 / silver 7 / passing 5 / in-progress 2 /
   none 0). Work the high-weight zero/negative checks first.
4. **Go fuzzing = cheapest Fuzzing 10.** Two or three `FuzzXxx(f
   *testing.F)` targets on pure validation functions beat any framework
   install. Seed corpus with real edge shapes, then REAL-fuzz locally
   (`go test -fuzz FuzzXxx -fuzztime 15s`) before pushing — seed-run green
   proves nothing about the fuzz body. Report exec counts + crashes found.
5. **Fuzz test files hit the same lint wall as all test files.** Lint rules
   forbidding internal-package tests (testpackage), high cognitive
   complexity, and flag parameters apply. Escape hatch for unexported
   targets: a linter-whitelisted `export_test.go` (`var XFn =
   unexportedFunc`) consumed by the external-package fuzz file; extract
   assertion bodies into helpers; pass values, not booleans. Run the repo
   linter locally before pushing — CI lints test files too.
6. **Pin every GitHub Action to a peeled commit SHA with a version
   comment** (`uses: owner/action@<full-sha> # v1.2.3`) — Pinned-Dependencies
   scores actions too, and mutable tags are a supply-chain hole adopters
   notice. Dependabot keeps the pins fresh afterward.
7. **Signed releases without a signing key: cosign keyless.** In the
   release workflow: `id-token: write` permission, `cosign sign-blob --yes
   --output-signature f.sig --bundle f.bundle` per artifact; verifiers use
   `--certificate-identity-regexp` anchored to the repo. This feeds
   Signed-Releases without any stored secret.
8. **CII badge = user registers, agent preps.** No workflow can create the
   bestpractices.dev entry (account + questionnaire). Before the user
   registers, audit which questionnaire criteria the repo already satisfies
   (public VCS, tagged releases, PR-based change control, static analysis,
   CI tests, pinned deps, security policy) and hand them the gap list — the
   jump from 0 to "in progress" (2 pts) is one signup; passing (5 pts) is
   realistic for a well-tooled repo.
9. **Verify maturity claims live after merging.** Re-read the scorecard
   API for the flipped check, confirm the badge endpoint resolves, confirm
   the release artifact + `.sig`/`.bundle` exist on the release page — a
   merged PR is not a moved metric.

## Project configuration (wire-up before any scores move)

The scorecard API only reports a repo that is public **and** has a
Scorecard run — a new repo scores nothing until configured. Do the
agent-side wiring as one PR, the user-side clicks in one message. Full
templates and click-paths live in `references/` — copy, don't
reconstruct:

- `references/scorecard-workflow.md` — complete scorecard.yml + badge
- `references/dependabot-config.md` — dependabot.yml ecosystems + grouping
- `references/security-policy.md` — SECURITY.md placement + reporting link
- `references/user-side-checklist.md` — Settings click-paths (branch
  protection, secret scanning, Dependabot alerts, CII registration)

Decision points here; the files carry the exact YAML and paths.

## Pitfalls

- A green CI matrix is false comfort when the workflow's GOTOOLCHAIN is
  `auto`: a dep that raises the `go` directive makes every matrix job
  silently download the new toolchain and "test 1.21–1.24" all actually run
  one version. Audit the go-directive floor (`go list -m` per dep) on any
  grouped dependabot bump; grouped "minor-and-patch" PRs smuggle
  directive-breaking transitive upgrades (x/text is a repeat offender).
- Scorecard's Signed-Releases needs signed artifacts on recent releases;
  a signing workflow that never ran scores −1. Merging the workflow is the
  start, the first gated release is the payoff.
- Manual release paths (`git tag` + push, `gh release create`) are NOT
  blocked by any release workflow — GitHub has no native tag-level
  "only if CI green" rule. Present tag-protection + a gated workflow as the
  closest approximation, and say plainly it does not restrict admin hands.
- Never claim a score "will improve" from a merge — quote the live API
  before and after; Scorecard's public report updates lag merges by hours.