# Security policy (SECURITY.md)

Feeds the Scorecard Security-Policy check. Valid locations, in order of
convention: repo root `SECURITY.md`, `.github/SECURITY.md`,
`docs/SECURITY.md`. Anywhere else = check scores 0.

## Minimal working template

```markdown
# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| latest release | yes |
| older releases | no |

## Reporting a vulnerability

Do NOT open a public issue for security reports.

Use GitHub private vulnerability reporting:
<https://github.com/<owner>/<repo>/security/advisories/new>

Include: description, reproduction steps, affected versions, impact.
You will get an initial response within 7 days.

## Disclosure policy

We coordinate a fix and release before any public disclosure.
Credit reporters in the release notes unless anonymity is requested.
```

## Notes

- The private-advisory URL works only if the repo has private vulnerability
  reporting enabled (Settings → Code security → Private vulnerability
  reporting). Enable it in the same round as the file lands, or the link
  404s for the first reporter.
- The check requires the file to contain at minimum: an address where
  vulnerabilities can be reported and a supported-versions statement.
  A one-line "email us" file without versions scores partial.
- Version support table must match reality: claiming support for versions
  with no release branch is a trust smell reviewers catch.
