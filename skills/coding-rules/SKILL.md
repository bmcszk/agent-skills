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
- A fluent or DSL call chain that already names its phases (given/when/then, arrange/act/assert) needs no phase-marker comments — the marker duplicates the name one line above it. Local style can override: when sibling files across the repo carry the markers, either purge repo-wide in one scoped round or leave all of them; purging only the files you touch splits the convention.

## Duplication

- Before writing a getter or small function, check whether a sibling already differs from it by one value — extract the shared shape into one primitive and make each sibling a one-line call (eight pick-or-fallback getters collapse into one chooser + eight one-liners).
- When two sibling entry points open with the same load-and-handle-error preamble, hoist the preamble into one helper; the entry points keep only their differing decisions.
- An inline closure that names a concept (build this value) becomes a named function so the caller reads as intent; an anonymous one-off that stays inline must still read in one breath.

## Refactor gate

- A style refactor proves behavior-unchanged with the repo's own gates before push (build + linter + full test suite), reports the diff as a per-file net LOC delta, and touches no test files when the task says impl-only — existing tests then bound the design, so read what they assert BEFORE choosing a shape.
- When a test asserts error text a dedupe changed, restore the missing part instead of editing the test (wrap with `%w` and append the exact suffix the test greps for).
- Commit each file/batch separately and keep the gates green between commits; push once to one PR — a broken intermediate commit breaks bisect, and CI watches the branch so local green between commits is what you control.
- Survey mechanically before reading files: functions over ~50 lines, sibling branches ending in the same finalize-and-return block, repeated call-then-wrap-err prologues, underscore-prefixed names, narration comments. Then read only the flagged files.
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

## Conflict order

When rules conflict, safety wins first, then local consistency, then good practice, then minimal change.

## Guards and gates: honest work only (user rule)

Rules are language-agnostic; tool names in the examples are Go ecosystem instances of the class.

Never work around a guard, gate, hook, or check: fix the work the gate
is rejecting. Concretely, in any language and repo:

- Never delete, skip, weaken, or comment out a test to make a suite pass.
  A test that fails because the world changed gets UPDATED to the new
  correct expectation with the reason recorded: never removed silently.
- Never turn off a lint rule, remove a linter from config, or narrow a
  check's scope so the violation stops being reported.
- Never use a suppression marker (`// nolint`, `//gosec:ignore`,
  `@ts-ignore`, `# noqa`, `#[allow]`, `#[expect]`, or your language's
  equivalent) to silence a gate. If the tool flags a real problem, fix the code. If it flags a
  false positive, fix the code so the tool agrees: or raise the
  config change as an explicit, recorded decision (never a drive-by).
- Never bypass hooks (`--no-verify`, `HUSKY=0`, a disabled CI step, or
  your stack's equivalent) or restructure a command so the gate does not
  run.
- A red gate is INFORMATION: report the exact output, fix the root
  cause, re-run. Working around the gate hides the problem from the
  next session and the next reviewer: the defect ships anyway.
- If a guard itself is wrong (blocks legitimate work), surface that as
  a decision for the user (grilling session) with the evidence; do not
  neutralize it unilaterally.
- The honest fix for a complexity lint on table subtests is restructuring:
  split each subtest case into its own top-level test function (Go
  example: each `t.Run` becomes `TestX_SubtestName`; a bare `{ }` block
  preserves variable scope during the split). Every assertion survives, the linter passes, no suppression
  marker. Do the restructure at the moment you would have typed the
  nolint: a marker first with cleanup scheduled never happens.
- Calibration exclusions go in the linter CONFIG as explicit recorded
  decisions, never as drive-bys: when a test spy must implement a fixed
  upstream interface whose signature carries a bool flag or unused
  parameter (e.g. an SDL event consumer), the rule is calibrated for
  production dispatch code and mis-fires on the stub. Add a scoped
  `exclusions` rule (test-file path filter + the specific linter + message
  text; Go example: path `_test\.go$` + linter `revive` + `text:`) with a comment stating WHY the signature is
  fixed, and match on the message text: a `text:` exclusion that
  doesn't match the linter's actual message silently fixes nothing
  (verify with one lint run after editing config). Config-level `text`
  exclusions beat per-call-site helper gymnastics (boolToInt tables,
  string-slicing dispatch) that trade one lint hit for three worse
  ones.
- Example (Go, linter `revive`): `unnecessary-format` fires on
  `fmt.Errorf` with NO format verbs: convert to `errors.New` and drop the
  `fmt` import only when no other call site uses it. Converting one call to `errors.New`
  while `fmt` stays imported is fine; converting the import when a
  remaining call still needs it is a build break.

## File structure

Order top-level declarations like this:

1. Imports
2. Constants
3. Variables
4. Structs or classes, public first
5. Constructors, public first
6. Methods, public first

Keep this order when the language allows it, and adapt only where the language idiom requires.


## Unit tests: black box, three sections, no mocks (user rule)

- **Black box through public API.** Test a unit by calling its public
  functions and methods and asserting on observable results. Testing
  private helpers is allowed ONLY when the user explicitly asks for it.
  If a private function seems to need direct testing, that is a design
  signal: either its behavior is already covered through a public
  entry point, or it is doing too much.
- **Given / When / Then in every test.** Each test reads as three
  sections: GIVEN the initial state, WHEN the action under test runs,
  THEN the expected result holds. Express the structure through the
  code's own design (arrange-act-assert layout, builder or fixture
  functions named for the phase); when the language or test style
  cannot carry it structurally, mark the sections with comments. A
  test whose three phases cannot be pointed out is not finished.
- **Avoid mocks.** Prefer testing real behavior over mocked
  collaborators. If a unit test needs a mock to pass, that is usually
  a signal the interaction belongs in an integration test: rewrite the
  case as an integration test against the real collaborator instead of
  stubbing it. Mocks stay acceptable only for things you cannot run in
  a unit test at all (network, clock, randomness, hardware); keep even
  those thin.

## Fluent test DSLs (pointers)

Test-DSL constructor topology and redesign-pushback rules live with the
Go fluent-testing skill: `go-fluent-testing/SKILL.md` and
`references/fluent-testing-guideline.md`. The universal parts (structure
through design, smallest change, user sign-off on structural probes) are
covered by the sections above.

