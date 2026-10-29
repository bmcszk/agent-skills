---
name: skill-craft
description: Use when writing or editing any SKILL.md / agent skill file, deciding what goes in a skill body versus reference files, or reviewing a skill for quality. Covers description routing, progressive disclosure, and token budgets.
---

# Skill craft

A skill is a routing trigger plus the smallest procedure that fixes a
repeated failure. A shorter body that carries the same law wins: studies show standard-length
guidance outperforms exhaustive documentation, and loading one to three
skills beats flooding context.

## Description is routing, not documentation

The description is injected into the model's context for EVERY task; the
body loads only on match. Write it as a load condition, third person, with
triggers:

- Good: "Use when rebasing a feature branch that conflicts with master, or
  when CI fails after a merge."
- Bad: "This skill helps with git problems."

Include negative triggers for adjacent skills when confusion is likely
("not for X"). Off-target activation is the number one skill failure mode.

## The body: every line pays rent

**Low-context budget:** Always pass an explicit skill manifest to delegated
workers (pi: repeatable `--skill` flags); the contract is the manifest, and
the worker loads only what it declares. Disabling the runner's discovery
entirely (pi: `--ns`) is a mode choice, not the default: discovery off
isolates high-risk or unfamiliar-repo runs; discovery on lets same-domain
ambient skills load additively around the explicit manifest.

1. Procedure the model cannot infer: exact commands, order, decision points.
2. Institutional context it has no way to know: names, paths, conventions.
3. Gotchas with a mechanism: "do X because Y fails otherwise". A gotcha
   without its why is a rule; with the why it survives edge cases.

## Progressive disclosure

One `SKILL.md`, plus reference files one level deep. The body states WHAT
and WHEN; references hold HOW-much-detail. Every reference is named in the
body with its load condition ("when the run times out, read
references/timeouts.md"), and every named file exists: a reference the
body never points to is dead, and a body pointing at a missing file
dead-ends the run that needs it. A generic example name in the body counts
as a dangling reference to a linter; write examples as "when X, read
references/<actual-file>.md".

Scripts beat prose for anything mechanical: a checked script enforces what
a paragraph only suggests.

**Gateway plugins as hard enforcement:** When a rule is violated repeatedly
(e.g., citation audit, git safety), move it from prose into a Hermes plugin
(`pre_tool_call` hook). The plugin blocks the tool call at the gateway level
so the model never sees the violating result. Reference: `hermes-plugin-dev` skill and
`pi-delegation` plugin pattern.

## Slim by moving, not by deleting law

When a body is over budget, the move is mechanical: procedures only some
runs need (recovery recipes, latency profiles, verbatim clauses) go to a
reference file, and the body keeps one line naming the file plus its load
condition ("on timeout, read references/timeouts.md" in the abstract; every
named reference must exist in the skill directory). A hard rule stays in
the body even if it costs tokens: moving a rule into a sometimes-loaded
file means a low-context dispatcher breaks it on the runs that skip the
file. Before finishing a slim-down, grep the body for `--flags` and verify
each exists in the tool's argparse: a doc that names a flag the client
cannot pass dead-ends every dispatcher after it.

## Style

- Imperative voice, no narrative. "Run X. If it fails, do Y."
- Third person in frontmatter; consistent terminology everywhere (pick one
  name for each thing; never synonym-cycle). Before adding a rule that
  names an artifact, grep the sibling skills it composes with and reuse
  THEIR term (the ecosystem's word for the plan-of-record, the unit of
  work, the gate), even if a different word reads better in isolation.
- No dates, ticket ids, or incident stories: the rule must stand alone.
- No em dashes; no AI filler (crucial, delve, additionally, "not just X but
  Y"). Requirements override style on any conflict.
- Spell-check compound words a linter will not catch ("misplaced", not
  "mis-placed"); a typo inside a normative rule undercuts the rule.

## Test before shipping

Load the skill in a fresh session on the task it targets; compare with and
without. A skill that only sounds right has never run. Check: does the
description route the right tasks in and the adjacent tasks out? Can a
model with no other context follow the body start to finish? Edit behind
that comparison, never by feel.

See references/eval-patterns.md for the matched-comparison shape and
references/pr-review.md for the mechanical review gates used when
reviewing a PR that changes skills.

## Mechanical quality gate for skill libraries

When reviewing multiple skills at once, run a checked lint script rather
than ad-hoc checks. The script should:
1. Parse frontmatter and body; validate YAML on every skill.
2. Flag descriptions missing "Use when" load triggers (routing).
3. Scan body for em dashes, the banned filler words listed in the
   Style section, first-person narrative.
4. Detect dates, ticket IDs, incident refs in body (not frontmatter metadata).
5. Verify every `references/<file>.md` and `scripts/<file>.py` named in body exists.
6. Normalize style (em dash → hyphen) before comparing content deltas.

Then classify findings:
- **Hard blockers** (dangling refs, broken frontmatter, dates/ids in body) → fix immediately.
- **Style sweep** (em dashes, AI filler, first-person headers) → mechanical replace across all files.
- **Routing** (descriptions not starting with "Use when/for") → rewrite as load conditions.
- **Content deltas** (install-only sections not in repo) → extract exact sections and add to repo skills.

After fixes: re-run lint, verify YAML, ensure line budgets < 500. Only then commit/PR.


## Combined PR pattern

When multiple open PRs target the same skill family, merge into one branch from origin/master:
1. `git checkout -b combined/<topic> origin/master`
2. `git diff origin/master..<pr1-branch> -- skills/ | git apply --3way`
3. `git diff origin/master..<pr2-branch> -- skills/ | git apply --3way`
4. Resolve conflicts (keep one copy of duplicated sections)
5. Close old PRs with `--delete-branch`; create single combined PR

## Install delta sync pattern

To sync content from ~/.agents/skills that diverged from repo:
1. Export origin/master tree: `git archive origin/master skills | tar -x -C /tmp/master-skills`
2. Normalize both sides (em-dash → hyphen) and diff install vs master per skill
3. Filter style-only diffs (em-dash, description wording, first-person headers)
4. Keep install-only content deltas (new sections, rules, procedures)
5. Apply deltas onto clean master branch; push as single PR
