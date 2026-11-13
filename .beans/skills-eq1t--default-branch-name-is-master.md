---
# skills-eq1t
title: Default branch name is master
status: completed
type: task
priority: normal
created_at: 2026-11-11T13:54:34Z
updated_at: 2026-11-13T00:08:55Z
---

Standing rule: the default/integration branch name is master (not main). Scripts, CI configs, docs, and branch recipes reference master.

## Triage: Standing rule. Destination: git SKILL.md intro (the one-line law above the fold). Docs-only; prose gate.

## Progress log: law placed in skills/git/SKILL.md intro (branch skills/bean-rules-harvest)

## Summary of Changes
master-is-default law placed in skills/git/SKILL.md intro (branch skills/bean-rules-harvest).

## Proof of Work
uvx skillscheck skills/ -> 36 skills, 0 errors, 0 warnings
skill-lint.py skills/ -> 0 skills with style findings
Law verified present in the target SKILL.md by read-back.

Residual: none.
