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
- `references/github-badges.md` — full README badge family (workflow
  status, coverage-via-gh-pages recipe, scorecard/pkg.go.dev/license/CII)
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
- Never trust a mutable `uses:` ref to resolve: some actions publish no
  resolvable major tag (`scorecard-action@v2` fails at workflow-parse time
  with "unable to find version"). Resolve every action to a peeled commit
  SHA via the GitHub API before pushing — annotated tags need a second hop
  (`GET /git/tags/<sha>` peels to the commit; `/git/ref/tags/x` may return
  the tag object, not the commit).
- Security-scanner actions ship their own toolchain: gosec's docker image
  bundles a Go release that must be ≥ the module's `go` directive, and
  `GOTOOLCHAIN=auto` in the workflow does not reach into the action
  container — an older gosec parses nothing and fails with "package
  requires newer Go version". Bump to a gosec whose image matches the
  module floor.
- When the user cites a sibling repo as the standard ("configure it like
  <other-repo>"), diff `.github/workflows/` of both repos first and port
  the same jobs/pins — describing security checks from memory produces a
  workflow that misses what the sibling actually runs.
- Badge row is guilty until verified: fetch each badge SVG live and read
  its `<title>`/`aria-label` (a 200 response can still say "failing",
  "not found", or "retired" — Go Report Card is a sunset service and its
  badge can never show green; remove it). pkg.go.dev's badge SVG is
  icon-only (no text/aria-label): verify the module link by curling the
  module page (expect 200), not the SVG.
- Verify the badge-publish pipeline end-to-end once (seed gh-pages as an
  orphan branch holding only `badges/*.json`, trigger the workflow, curl
  the raw JSON and the shields endpoint) — a badge URL that returns 200
  with placeholder content is still a broken badge. Coverage badge reads a
  gh-pages JSON that does not exist until the first push of the publishing
  workflow — and that push 403s until BOTH the job has `contents: write`
  and the repo's Settings→Actions default GITHUB_TOKEN permission is
  `write`. shields `endpoint` badges lag the gh-pages JSON by minutes (CDN
  caches both): verify the raw JSON by commit SHA first, then treat a
  stale shields render as propagation delay, not a broken pipeline.
- A failing PR check named "Scorecard" that is NOT the security.yml job is
  the code-scanning alert-delta check (app `github-advanced-security`): it
  re-reports open Token-Permissions/Pinned-Dependencies alerts as PR
  failures until the next scorecard analysis re-scans the fixed workflows.
  Clear the underlying alerts repo-wide — permissions block on EVERY
  workflow, SHA-pin EVERY workflow including release-only ones; the
  check-run rerequest API 404s because it is not a workflow check.
- Scorecard's Token-Permissions check fails any job carrying `contents:
  write` that also does test work. Split publishing into its own job
  (`needs: test`, default-branch-only) holding the single write grant,
  outputs via `upload-artifact`/`download-artifact`; the test matrix stays
  read-only — granting the test job write fixes one check by failing the
  other, so the job split is the only shape satisfying both.
- Dependabot PRs can look hopelessly red when their check runs are STALE —
  weeks-old failures from before a master lint/CI fix. Before diagnosing an
  old PR, compare the check-run date to master's recent history; if stale,
  force fresh runs first (`gh pr update-branch`, or `@dependabot rebase`
  when the branch touches workflows your token can't edit) and only then
  root-cause the NEW verdict.
- A dep bump that raises its own minimum `go` above the module's floor is
  unmergeable by construction — close it with the proxy-proven evidence
  (`curl https://proxy.golang.org/<mod>/@v/<ver>.mod`, the `go` line) and
  the newest compatible version, instead of chasing CI green on every
  matrix leg. Bumping the module's Go floor is an owner policy call, never
  smuggled in via Dependabot.
