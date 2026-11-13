---
# skills-c8at
title: 'Starting new dev work: ensure base branch is up to date'
status: in-progress
type: task
priority: normal
created_at: 2026-11-11T13:54:34Z
updated_at: 2026-11-12T23:59:38Z
---

Standing rule: before starting any new dev work, ensure you are up to date - e.g. a new branch comes from master only after master itself is current (fetch + ff-only pull of origin master first). Never branch from a stale local base.

## Triage: Standing rule. Destination: git SKILL.md start-of-work section; the freshness guard names the failure mode (branching from a stale base). No code, docs-only: TDD inapplicable; gates are skill-lint + skillscheck.

## Progress log: law placed in skills/git/SKILL.md (stale-base guard) (branch skills/bean-rules-harvest)
