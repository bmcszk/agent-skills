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

Calibrate both directions: an under-specified description misses valid
tasks, an over-broad one triggers noise. Test with two prompt sets - ones
that must trigger it, near-misses that must not - and edit until both
route correctly. Trivial one-step tasks never trigger skills regardless
of wording; the description targets work that needs this procedure.

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

## The knowledge delta test

A skill must change behavior: non-obvious decision criteria, trade-offs
tied to conditions, failure modes learned in practice, domain procedures
whose ordering matters. Generic advice the model already supplies ("write
clean code", basic tutorials) is dead weight no matter how correct.

## Freedom calibration

Match instruction rigidity to task fragility, not to writing mood.
Creative work needs principles and examples, not a fixed script; review
and design work needs decision criteria with moderate freedom; fragile
operations (file edits, security, migrations, external writes) need
explicit step sequencing with verification. A skill that scripts the
creative parts and vibes the dangerous parts fails both ways.

## Progressive disclosure

One `SKILL.md`, plus reference files one level deep. The body states WHAT
and WHEN; references hold HOW-much-detail. Every reference is named in the
body with its load condition ("when the run times out, read
references/eval-patterns.md"), and every named file exists: a reference the
body never points to is dead, and a body pointing at a missing file
dead-ends the run that needs it. A generic example name in the body counts
as a dangling reference to a linter; write examples as "when X, read
references/<actual-file>.md".

Reading a reference costs its tokens only when read, so references may be exhaustive: full API dumps, long examples, checklists. Keep each one
single-concern and named by content (`form_validation_rules.md`, not
`doc2.md`); split by domain (`reference/aws.md`, `reference/gcp.md`) so a
run loads only its domain. Above 300 lines, add a table of contents.

Scripts beat prose for anything mechanical: a checked script enforces what
a paragraph only suggests, and running one costs its output tokens, not
its source. State execution intent explicitly ("run", not "you could").

**Gateway plugins as hard enforcement:** When a rule is violated repeatedly
(e.g., citation audit, git safety), move it from prose into a Hermes plugin
(`pre_tool_call` hook). The plugin blocks the tool call at the gateway level
so the model never sees the violating result. Reference: `hermes-plugin-dev` skill and
`pi-delegation` plugin pattern.

## Slim by moving, not by deleting law

When a body is over budget, the move is mechanical: procedures only some
runs need (recovery recipes, latency profiles, verbatim clauses) go to a
reference file, and the body keeps one line naming the file plus its load
condition ("on timeout, read references/eval-patterns.md" in the abstract; every
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

## Portability: project, agent, and model agnostic

A skill must run identically on any repo, any agent runtime, any model.
The test for every line:

- Project agnostic: no repo names, machine paths, or team-specific
  tooling in rules. Write "the project's lint gate", not the tool's
  proper name; keep concrete paths in examples, not law.
- Agent agnostic: describe capabilities, not clients. "Run the project's
  build command" beats a runner-specific command; quarantine unavoidable
  client incantations in a reference the body does not require.
- Model agnostic: procedures must survive a small model. One instruction
  per line, explicit 1-2-3 ordering, no "simply" or "obviously". Anything
  a weak model would skip gets a gate (script, checklist) instead of
  prose, and every hard rule explains its why so any model generalizes.
- The skill spec (frontmatter name + description, body, optional
  scripts/references/assets) is the portability contract. Runtime
  extensions (gateway hooks, runner flags) must degrade gracefully when
  absent.

## Test before shipping

Load the skill in a fresh session on the task it targets; compare with and
without. A skill that only sounds right has never run. Check: does the
description route the right tasks in and the adjacent tasks out? Can a
model with no other context follow the body start to finish? Edit behind
that comparison, never by feel.

See references/eval-patterns.md for the matched-comparison shape.

## Mechanical quality gate for skill libraries

Run two gates, in this order:

1. **Structural gate: `skillscheck`** (`uvx skillscheck <skills-dir>`).
   Owns everything the spec and cross-agent reality can check: frontmatter
   validity and metadata value types, unclosed code fences, broken links
   with fragment anchors, token budgets, reference nesting, secret leaks,
   orphaned files, and per-agent adapter rules. Do not hand-write these
   checks; a checked script you maintain loses to a maintained linter.
   `--strict` promotes warnings to errors in CI.
2. **Style gate: `scripts/skill-lint.py`** (this skill). Owns only what an
   external linter cannot know: the local prose law (em dashes, AI filler,
   first-person narrative) and project-content leakage (dates, ticket
   ids, incident refs, bean ids in body).

Then classify findings:
- **Hard blockers** (dangling refs, broken frontmatter, dates/ids in body) → fix immediately.
- **Style sweep** (em dashes, AI filler, first-person headers) → mechanical replace across all files.
- **Routing** (descriptions not starting with "Use when/for") → rewrite as load conditions.
- **Content deltas** (install-only sections not in repo) → extract exact sections and add to repo skills.

After fixes: re-run both gates, verify YAML, ensure line budgets < 500.
Only then commit/PR. Third-party installed skills: report upstream-owned
findings, never fix in place (sync reverts them); archive dirs live
outside the skills root or the linter scans them.

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
