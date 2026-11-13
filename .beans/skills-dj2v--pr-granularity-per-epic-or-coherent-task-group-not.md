---
# skills-dj2v
title: 'PR granularity: per epic or coherent task group, not per feature/task'
status: completed
type: task
priority: normal
created_at: 2026-11-10T16:29:32Z
updated_at: 2026-11-13T00:08:55Z
---

Standing rule for this repo's PR flow: do NOT open one PR per beans feature/task. One PR per epic; if an epic is too big, one PR per reasonably similar task group. Keeps review rounds and CI runs proportionate to the work.

## Triage: Standing rule. Destination: git SKILL.md PR-granularity law in open-real-PRs section. Docs-only; prose gate.

## Progress log: granularity law placed in skills/git/SKILL.md (branch skills/bean-rules-harvest)

## Summary of Changes
Per-epic granularity law placed in skills/git/SKILL.md (branch skills/bean-rules-harvest).

## Proof of Work
uvx skillscheck skills/ -> 36 skills, 0 errors, 0 warnings
skill-lint.py skills/ -> 0 skills with style findings
Law verified present in the target SKILL.md by read-back.

Residual: none.
