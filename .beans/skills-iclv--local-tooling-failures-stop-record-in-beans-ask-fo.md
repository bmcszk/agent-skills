---
# skills-iclv
title: 'Local tooling failures: stop, record in beans, ask for help, wait'
status: completed
type: task
priority: normal
created_at: 2026-11-12T12:55:59Z
updated_at: 2026-11-13T00:08:55Z
---

Standing rule when local tooling fails (build tools, linters, package managers, CI runners on this machine): STOP the current work path. If a beans task list exists for the affected project, add the tooling issue to that list as a bean. Then ask the user for assistance and WAIT for the fix - do not work around, patch, or bypass broken local tooling on your own.

## Triage: Standing rule. Destination: keep-on-going stop conditions (tooling failure is the stop-ask-wait exception). Docs-only; prose gate.

## Progress log: law placed in skills/keep-on-going/SKILL.md stop conditions (branch skills/bean-rules-harvest)

## Summary of Changes
Stop-ask-wait law placed in skills/keep-on-going/SKILL.md stop conditions (branch skills/bean-rules-harvest).

## Proof of Work
uvx skillscheck skills/ -> 36 skills, 0 errors, 0 warnings
skill-lint.py skills/ -> 0 skills with style findings
Law verified present in the target SKILL.md by read-back.

Residual: none.
