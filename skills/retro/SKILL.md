---
name: retro
description: >-
  Conduct a retrospective on a coding session: mine what happened for
  environment improvements, not blame. Use when a finished task, wave, or
  session needs its lessons captured as process improvements.
license: MIT
metadata:
  audience: agents
  workflow: review
  category: meta
  technologies: retrospectives, process
---

# Retro

A retrospective improves the agent's environment so future runs fail
less: navigation, checks, standards, tooling. Read the session's
primary sources first (logs, transcripts, diffs); default to the
current session when none is named.

## Candidate categories

Judge the session against each category and collect findings.

- Navigation: how hard was it to find the right files? Hidden
  dependencies between files, long searches for one fact. The fix is
  a navigation pointer where the search started.
- Automated checks: mistakes an existing check could have caught?
  Read the repo's own check commands and CI first: a check that
  exists but sits unwired or silently broken is the finding, not a
  reinvention. A repo with no guardrail at all (no pre-commit hook,
  no CI running lint, types, or tests) is itself a finding.
- Coding standards: should the reviewer gain a new rule, lose one, or
  get one clarified? Classify first: a mechanical violation (fixed
  pattern, banned API, import shape, file location) gets a
  deterministic check in the repo's linter, a pre-commit hook, or a
  CI job, whichever is cheapest; default to building the check over
  writing the rule. Reserve the standards document for judgement
  calls no guardrail could substitute.
- Steering bloat: instructions in guidance files that change no
  behavior. Dead steering words dilute live ones.
- Tool economy: expensive tool calls that a command flag, a batched
  call, or a small script would have avoided.
- Information access: facts the agent needed but could not reach.
  Teeing logs, read-only access to a service, an exposed state file.

## Implementation vs review

All work runs in two stages. The implementing agent carries the most
context pressure: exploration, writing, debugging. The reviewing
agent carries the least: it receives a diff with no exploration. So
standards enforcement belongs to review, not implementation.

## Output

Present the findings to the user in order of severity: the finding,
the evidence from the session, the proposed fix, and who owns it
(a check to build, a rule to write, a pointer to add).
