---
# skills-16zd
title: Migrate communication skill to global skills
status: draft
type: task
priority: normal
created_at: 2026-11-12T13:03:40Z
updated_at: 2026-11-12T16:57:52Z
---

Hermes currently uses the hermes-side communication skill; migrate it to the global skills tree (agent-skills repo). Rules the skill must encode: absolute honesty; simple language; use English, and switch to Polish only when explicitly told - no other languages; check before assume; research before claim; TLDR section at the end, max 3 sentences.

Scope also includes: removal of the Hermes-side communication skill (~/.hermes/skills/communication/) and updating ALL references to it across configs and skills, repointing them from hermes to the global skill.
