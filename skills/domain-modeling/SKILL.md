---
name: domain-modeling
description: >-
  Build and sharpen a project's domain model: glossary terms and
  architecture decisions recorded the moment they settle. Use when
  discussing codebase terminology, writing or editing a glossary, or
  recording a decision record.
license: MIT
metadata:
  audience: agents
  workflow: design
  category: meta
  technologies: glossary, adr, domain-driven design
---

# Domain modeling

Sharpen the project's domain model while designing: challenge terms,
invent edge-case scenarios, write the glossary and decision records
the moment they crystallise. Reading the glossary for vocabulary is a
one-line habit; this skill is for changing the model.

## File structure

A single-context repo keeps `GLOSSARY.md` at the root and decisions
in `docs/adr/`. A multi-context repo keeps a `GLOSSARY-MAP.md` at the
root pointing to each context's own glossary and ADR dir. Create
files lazily: the glossary appears when the first term resolves, the
ADR dir when the first record is needed.

## During the session

- Challenge against the glossary: a term that conflicts with the
  recorded language gets called out immediately, with both meanings
  stated side by side.
- Sharpen fuzzy language: an overloaded term gets split into precise
  candidates and the user picks one.
- Discuss concrete scenarios: stress-test stated relationships with
  specific edge cases that force the boundaries between concepts to
  be precise.
- Cross-reference with code: when the user states how something
  works, check the code agrees, and surface contradictions with both
  halves quoted.
- Update the glossary inline when a term resolves. Never batch.
  The glossary holds terms and meanings only: no implementation
  detail, no scratch notes, no decisions. Term format, the Avoid
  list, and the single vs multi-context map layout: read
  [references/glossary-format.md](references/glossary-format.md) when
  writing or editing a glossary.

## Decision records

Offer a record only when all three hold:

1. Hard to reverse: changing the mind later costs meaningfully.
2. Surprising without context: a future reader will ask why.
3. A real trade-off: genuine alternatives existed and one was picked
   for stated reasons.

Missing any of the three: skip the record.

Record format, numbering, and optional sections: read
[references/adr-format.md](references/adr-format.md) when writing a
decision record.
