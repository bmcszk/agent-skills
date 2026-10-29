# Reference patterns and sources

## Matched comparison (the eval gate)

Run the target task twice in fresh sessions: once with the skill available,
once without. Score the with-skill run on the specific failure the skill
exists to fix. Accept an edit only when the with-skill run beats the
without-skill run on that failure; otherwise the skill is decoration.

Shape:

1. Task: the real task, not a toy (a real repo, a real failure).
2. Without: fresh session, skill absent. Record the failure.
3. With: fresh session, skill loaded. Record the same steps.
4. Diff: does the skill change behavior on the failure path? If both runs
   behave the same, the skill is not routing or not read.

## Negative evals (off-target routing)

List the adjacent tasks the skill must NOT capture. Load the skill in a
session running one of those tasks; if it activates, sharpen the
description's triggers or add the negative trigger line.

## Slim-down review (two-skill family check)

When editing one skill of a pair that composes (planner/executor, standard/amendment),
check three things before calling it done:

1. Duplication: a rule stated normatively in both files. Keep the rule in
   the file that owns the decision; the other file carries the mechanic or
   a pointer.
2. Cross-references: neither file names or links the other. Two skills that
   compose through a shared artifact (a checklist, a contract file) need no
   direct references; the shared artifact is the interface.
3. Example pairs: any rule a worker can violate in prose (comment style,
   report shape) ships with a compliant/violating example pair from the
   target repo, not prose alone. Prose-only rules get pattern-matched and
   pass gates while violating intent. A cited pattern
   (`TODO ... lands later (<id>)`) plus a one-line deletion example is
   enough; the violating example is what makes a gate checkable.
4. Prerequisite-only content: material that exists only because another
   skill or gate needs it (enforcement mechanics, shared gate recipes)
   goes in the skill that owns the enforcement, with the content skill
   keeping a one-line "enforced by <gate>" pointer. Split it the other
   way and both files are half-procedures.
5. Amendment-wrapper absorption: when a base skill gains a rule that a
   hermes-local `<name>-notes` wrapper also carries, the wrapper drops
   its copy in the same pass; a rule stated normatively in the base
   and the wrapper is the duplication case of item 1.

Replay each fix against the earliest point it would fire: a rule that first
fires at review stage, after the full wave shipped, is a detector, not a
prevention. Move it earlier (canary, contract) until it catches the failure
at file one.

## Sources

- Anthropic, "Equipping agents for the real world with Agent Skills"
  (2025-10-16) and "Skill authoring best practices" (platform.claude.com):
  progressive disclosure, <500-line bodies, concise-is-key, one-level
  references, scripts over prose, degrees of freedom.
- Perplexity, "Designing, refining, and maintaining Agent Skills" (2026):
  description as routing trigger, "Load when...", off-target activation as
  the top failure mode, evals before the skill, gotchas as core content.
- Arize, "How to write effective AI agent skills" (2026, three studies):
  compact beats comprehensive; 1-3 loaded skills optimal; human procedural
  expertise over model-generated prose; eval-gated edits; test every
  model-harness pair.
