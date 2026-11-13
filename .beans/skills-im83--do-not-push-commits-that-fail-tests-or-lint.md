---
# skills-im83
title: Do not push commits that fail tests or lint
status: completed
type: task
priority: normal
created_at: 2026-11-12T14:57:24Z
updated_at: 2026-11-13T00:08:55Z
---

Standing rule: never push a commit that does not pass the project's test suite and linter. Green gates before push is non-negotiable - if tests or lint fail, fix them locally first.

## Triage: Standing rule. Destination: git SKILL.md CI-status bullet (green before push). Docs-only; prose gate.

## Progress log: green-push law placed in skills/git/SKILL.md (branch skills/bean-rules-harvest)

## Summary of Changes
Green-commits-before-push law placed in skills/git/SKILL.md CI bullets (branch skills/bean-rules-harvest).

## Proof of Work
uvx skillscheck skills/ -> 36 skills, 0 errors, 0 warnings
skill-lint.py skills/ -> 0 skills with style findings
Law verified present in the target SKILL.md by read-back.

Residual: none.
