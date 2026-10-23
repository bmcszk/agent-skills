---
name: coding-rules
description: >
  General, language- and project-agnostic coding style built around two rules:
  top-level functions read as intent and business sequence, and intent functions
  stay separate from implementation-detail functions. Also covers comments,
  minimal diffs, local style, conflict priority, and file layout. Use when
  writing, refactoring, reviewing, or structuring source code in any language
  or repository.
---

# Coding rules

These rules apply to any language and any project. Apply them to new code and to code you touch. Do not reshuffle unrelated code only to match them.

## Top-level function shows intent and business sequence

- The top-level function reads like the use case, as a short list of business steps in order.
- Each line calls a step named in domain words. Inline mechanics belong in a helper.
- A function stays at one level of abstraction.
- Error paths return early, so the happy path stays flat.

## Intent functions stay separate from implementation details

- Intent functions hold business decisions and their order. Keep them pure when practical, with no I/O.
- Mechanism functions handle I/O, serialization, retry, logging, concurrency, and framework glue. They make no business decisions.
- Intent functions call mechanisms. A mechanism never decides a business rule.
- Name intent functions by domain meaning and mechanisms by their technical job.
- Avoid vague names such as `utils`, `helpers`, `manager`, `process`, or `handle` unless the meaning is precise.
- Test the important decisions and edge cases in the intent functions.

## Before implementation

Write down briefly:

1. The use-case intent.
2. The business rules.
3. The side effects.
4. Which functions are intent and which are mechanisms.

## Comments

- Write no comments by default.
- Add one short line only when the code cannot show the point.
- A comment explains why, an invariant, a contract, or non-obvious behavior.
- Do not narrate, restate the code, or add obvious TODOs.
- When refactoring a block you touch, delete narration comments ("call X now", "this returns Y") in the same pass — a refactor that ships new structure under old narration leaves the file lying about itself.
- A doc comment that restates the function's name and signature is narration ("writeTempConfig writes YAML to a temp file and returns its path") — delete it; keep only the clause naming an invisible contract (fresh instance, isolation, wire format, poll-vs-sleep rationale).
- Phase-marker comments in tests (`// given`, `// when`, `// then`, or arrange/act/assert equivalents) are required structure, not narration. Keep them; add them when the three phases are not obvious from the test layout alone. This outranks "no comments by default" and "delete narration comments" when those rules would remove or skip the markers.

## Duplication

- Before writing a getter or small function, check whether a sibling already differs from it by one value — extract the shared shape into one primitive and make each sibling a one-line call (eight pick-or-fallback getters collapse into one chooser + eight one-liners).
- When two sibling entry points open with the same load-and-handle-error preamble, hoist the preamble into one helper; the entry points keep only their differing decisions.
- An inline closure that names a concept (build this value) becomes a named function so the caller reads as intent; an anonymous one-off that stays inline must still read in one breath.

## Refactor gate

- A style refactor proves behavior-unchanged with the repo's own gates before push (build + linter + full test suite), reports the diff as a per-file net LOC delta, and touches no test files when the task says impl-only — existing tests then bound the design, so read what they assert BEFORE choosing a shape.
- When a test asserts error text a dedupe changed, restore the missing part instead of editing the test (wrap with `%w` and append the exact suffix the test greps for).
- Commit each file/batch separately and keep the gates green between commits; push once to one PR — a broken intermediate commit breaks bisect, and CI watches the branch so local green between commits is what you control.
- Survey mechanically before reading files: functions over ~50 lines, sibling branches ending in the same finalize-and-return block, repeated call-then-wrap-err prologues, underscore-prefixed names, narration comments (not test phase markers: given/when/then, arrange/act/assert). Then read only the flagged files.
- Batch the round as one delegation with the file list, the survey hits, and the repo's protected invariants named per file (review-hardened logic, load-bearing error strings) — the delegate applies per-file changes, gates after each batch, and reports per-file net LOC deltas; re-run every gate yourself before trusting its report.
- When the user picks a subset of the skill's rules for the round (e.g. 'only comments + intent separation'), scope the round to exactly those rules and name the chosen rules in the delegation; a second pass over the same files is cheap, reverting an out-of-scope reshuffle is not.
- On 'fix every file one by one', have the delegate commit one file per commit in a stated order (simplest first) — batched commits blur which change broke a gate, and the user reads history per file.
- Refactoring code whose validation order tests pin (e.g. reject-before-build semantics) breaks tests even when each extracted helper is correct — read the test that pins ordering before moving any validation step.
- After a comment-deletion pass, re-check formatter/lint doc-comment rules on touched files: deleting one line can leave an exported symbol undocumented and fail a lint that passed before (e.g. revive in Go); a small follow-up commit restoring the doc line is expected, not a mistake.

## Minimal change

- Make the smallest readable diff that solves the request.
- Reuse code that already exists before you write new code.
- Do not add interfaces, factories, layers, files, or dependencies that the task does not need.
- Prefer explicit control flow over clever, compressed code.

## Local style

- Follow the patterns already in the file and the repository.
- Use the project's formatters, linters, and tests.

## Visibility

- Start each symbol at the tightest visibility the task allows (private, unexported, or module-internal) and widen only when a caller outside that boundary needs it.
- Export or make public only for real outside callers, not for possible future use.

## Conflict order

When rules conflict, safety wins first, then local consistency, then the rules in this skill, then minimal change. This skill outranks ponytail-style laziness or YAGNI-only shortcuts when those would violate a rule here.

## Guards and gates: honest work only (user rule)

Rules are language-agnostic; tool names in the examples are Go instances
of the class.

Never work around a guard, gate, hook, or check: fix the work the gate
rejects.

- Never delete, skip, weaken, or comment out a test to make a suite
  pass. A test failing because the world changed gets updated to the new
  correct expectation, with the reason recorded.
- Never turn off a lint rule, remove a linter from config, or narrow a
  check's scope so the violation stops being reported.
- Never silence a gate with a suppression marker (`nolint`, `@ts-ignore`,
  `# noqa`, `#[allow]`, or your language's equivalent). Real problem:
  fix the code. False positive: fix the code so the tool agrees, or
  raise the config change as an explicit recorded decision.
- Never bypass hooks (`--no-verify`, `HUSKY=0`, a disabled CI step) or
  restructure a command so a gate does not run.
- A red gate is information: report the exact output, fix the root
  cause, re-run.
- A guard that blocks legitimate work goes to the user as a decision
  with evidence; never neutralize it unilaterally.
- Complexity lint on table subtests: split each case into its own
  top-level test function (Go: `t.Run` case becomes
  `TestX_SubtestName`). Restructure at the moment you would have typed
  the suppression marker.
- Calibration exclusions live in linter config as explicit recorded
  decisions, never drive-bys: scope them (test-file path filter +
  specific linter + exact message text), comment why the signature is
  fixed, and verify with one lint run that the exclusion matches.

## File structure

Order top-level declarations like this when the language allows it (adapt only where the idiom requires):

1. Imports
2. Constants
3. Variables
4. Structs or classes
5. Constructors
6. Methods

Within a category, rank placement (stronger wins):

1. **Call order:** caller above callee; the file reads top to bottom in invocation order.
2. **Public before private:** only when call order does not already place the symbols — public before private at that level. Does not justify exporting more (see Visibility).
3. **Newer toward bottom:** when call order still does not decide, put newer code toward the bottom of the file or section.

## Unit tests: black box, given/when/then, no mocks (user rule)

- Test through the public API only; private helpers only when the user
  explicitly asks. A private function that seems to need direct testing
  is a design signal: either a public entry point already covers it, or
  it does too much.
- Every test reads as given / when / then. `given` is optional setup.
  `when` is mandatory: the action under test. `then` is mandatory:
  the asserted result. If you cannot point at the `when` or the
  `then`, the test is rewritten from scratch, not patched. Carry the
  structure through the code's design when possible; keep the
  phase-marker comments (see Comments).
- Avoid mocks: test real behavior. A unit test that needs a mock is
  usually an integration test in disguise: rewrite it against the real
  collaborator. Mocks stay only for what a unit test cannot run at all
  (network, clock, randomness, hardware), and stay thin.
