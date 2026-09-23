# User-side checklist (Settings clicks the agent cannot do)

Hand this list to the repo owner verbatim. Every item maps to a Scorecard
check; do them in this order (highest score-per-click first).

## 1. Branch protection (Branch-Protection check)

Settings → Branches → Add branch protection rule

- Branch name pattern: the default branch (`master`/`main`)
- Require a pull request before merging (any settings; approvals count
  only if >0 reviewers)
- Require status checks to pass: pick the test workflow's job name
  (must exist at least once before it can be selected — push once first)
- Optional: require signed commits, require linear history
- Do NOT tick "Restrict who can push" unless intentional — it locks out
  admins without a bypass role

Owner cannot be fully blocked by this (enforce_admins off = admins bypass;
GitHub has no tag-level CI gate — see SKILL.md pitfalls).

## 2. Secret scanning + push protection

Settings → Code security → Secret scanning → Enable
Settings → Code security → Push protection → Enable

Push protection blocks pushes containing detected secrets at client time.
Zero-score to full in one toggle.

## 3. Dependabot alerts + security updates

Settings → Code security → Dependabot alerts → Enable
Settings → Code security → Dependabot security updates → Enable

Feeds the Vulnerabilities check indirectly (it reads the OSV/dev.gost
databases for deps in the manifest); alerts are also what the
Dependency-Update-Tool check expects to see acted on.

## 4. Private vulnerability reporting

Settings → Code security → Private vulnerability reporting → Enable

Required for the advisory link in SECURITY.md (see
`references/security-policy.md`) to resolve.

## 5. CII Best Practices registration (CII-Best-Practices check)

1. Create account: <https://www.bestpractices.dev/>
2. Add project → paste repo URL (`https://github.com/<owner>/<repo>`)
3. Fill the self-certification questionnaire. Status `in progress` alone
   scores 2; `passing` scores 5; silver 7; gold 10.

Before starting, audit what the repo already satisfies so the questionnaire
is mostly confirmation: public VCS, version control (GitHub), unique
version tags, PR-based change control, static analysis (CodeQL/gosec/
govulncheck), CI test runs, pinned dependencies, SECURITY.md, signed
releases. The remaining genuine work is usually: project description
completeness, documentation links, documented test evidence.

Badge (any status) embeds as:

```markdown
[![CII Best Practices](https://bestpractices.dev/projects/<id>/badge)](https://bestpractices.dev/projects/<id>)
```

`<id>` appears in the project URL after registration.
