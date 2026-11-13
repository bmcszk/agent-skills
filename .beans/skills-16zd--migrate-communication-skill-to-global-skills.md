---
# skills-16zd
title: Migrate communication skill to global skills
status: in-progress
type: task
priority: normal
created_at: 2026-11-12T13:03:40Z
updated_at: 2026-11-13T00:08:55Z
---

Hermes currently uses the hermes-side communication skill; migrate it to the global skills tree (agent-skills repo). Rules the skill must encode: absolute honesty; simple language; use English, and switch to Polish only when explicitly told - no other languages; check before assume; research before claim; TLDR section at the end, max 3 sentences.

Scope also includes: removal of the Hermes-side communication skill (~/.hermes/skills/communication/) and updating ALL references to it across configs and skills, repointing them from hermes to the global skill.

## Triage: standing rule set for the global communication skill. Destination: new skills/communication/SKILL.md carrying the six rules plus the portable laws from the hermes-side original. Machine-side removal + reference repoint runs post-merge (the global skill must exist upstream first). Docs-only.

## Progress log: skills/communication/SKILL.md written on branch skills/bean-rules-harvest (gates 0/0). Machine-side step (remove ~/.hermes/skills/communication, repoint references, reinstall from repo post-merge) intentionally open until the PR merges.
