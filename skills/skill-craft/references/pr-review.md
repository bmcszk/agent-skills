# skill-craft PR review pattern

This file documents the mechanical review gates used when reviewing PRs to a skill repo.

## Mechanical gates (run first, no judgement)

1. **Budget** - body ≤ 500 lines; description ≤ ~600 chars.
2. **Routing** - description leads with a load trigger: "Use when", "Use for", "Load when", or "TRIGGERS -".
3. **Style** - zero em dashes; zero AI filler (crucial, delve, additionally, comprehensive, seamless, leverage, robust).
4. **Dates/IDs** - no PR numbers, ticket IDs, dates, or incident references in body (frontmatter metadata OK).
5. **First-person** - no narrative "I will/am" lines in body.
6. **Dangling refs** - every `references/foo.md` and `scripts/foo.py` named in body exists on disk.
7. **Terminology** - pick one word per concept; no synonym cycling (e.g., "epic body" everywhere, not sometimes "epic plan").
8. **Mechanism attached** - every rule carries its WHY (the failure mode it prevents).

## Substantive gates (read + think)

- **Example pair** - a prose rule a worker can violate must ship a compliant/violating example pair from the target repo, not prose alone.
- **Duplication with amendment wrappers** - if a wrapper (`<name>-notes`) already carries the rule normatively, the upstream PR must land it; then the wrapper drops the amendment (per maintenance rule).
- **Vendor agnosticism** - no Hermes, Cline, brainer, pi, specific model snapshots, or absolute paths in body text.

## Review flow

```bash
python3 scripts/skill-lint.py /path/to/skills   # mechanical
# read diff; check substantive gates
```

## Anti-pattern: "looks right" without running lint

A skill that only sounds right has never run. Always run the lint script before approving.
