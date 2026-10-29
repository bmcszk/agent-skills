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

- The top-level function reads like the use case: a short list of business steps in order.
- Each line calls a step named in domain words. Put the mechanics in a helper.
- Keep a function at one level of abstraction.
- Return early on errors, so the happy path stays flat.

## Intent functions stay separate from implementation details

- Intent functions hold business decisions and their order. Keep them pure when you can: no I/O, no hidden state changes.
- Mechanism functions handle I/O, serialization, retry, logging, concurrency, and framework glue. They make no business decisions.
- Intent functions call mechanisms. A mechanism never decides a business rule.
- Name intent functions by domain meaning and mechanisms by their technical job.
- Do not use vague names: `utils`, `helpers`, `manager`, `process`, `handle`, unless the meaning is precise.
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
- Refactoring a block you touch? Delete narration comments ("call X now", "this returns Y") in the same pass. New structure under old narration leaves the file lying about itself.
- A doc comment that restates the name and signature is narration ("writeTempConfig writes YAML to a temp file and returns its path"). Delete it. Keep the clause naming an invisible contract (fresh instance, isolation, wire format, poll-vs-sleep reason).
- Phase markers in tests (`// given`, `// when`, `// then`, or arrange/act/assert) are required structure, not narration. Keep them; add them when the three phases are not obvious from the test layout alone. This outranks "no comments by default" and "delete narration comments" when those rules would remove the markers.

## Duplication

- Before writing a getter or small function, check whether a sibling already differs from it by one value. If so: extract the shared shape into one function, make each sibling a one-line call. Eight pick-or-fallback getters become one chooser plus eight one-liners.
- Two sibling entry points open with the same load-and-handle-error preamble? Move the preamble into one helper. The entry points keep only their differing decisions.
- An inline closure that names a concept ("build this value") becomes a named function, so the caller reads as intent. An anonymous one-off that stays inline must still read in one breath.

## Refactor gate

- A style refactor proves behavior did not change before push: build, linter, full test suite. Report the diff as a per-file net line count. Touch no test files when the task says impl-only. Existing tests then bound the design: read what they assert before choosing a shape.
- A test asserts error text that a dedupe changed? Restore the missing part in the code instead of editing the test. Wrap with `%w` and append the exact suffix the test greps for.
- Commit each file or batch separately. Keep the gates green between commits. Push once to one PR. A broken intermediate commit breaks bisect, and CI watches the branch, so local green between commits is what you control.
- Survey mechanically before reading files: functions over ~50 lines, sibling branches ending in the same finalize-and-return block, repeated call-then-wrap-err prologues, underscore-prefixed names, narration comments (test phase markers do not count: given/when/then, arrange/act/assert). Then read only the flagged files.
- If the round is delegated, batch it as one delegation: the file list, the survey hits, and the repo's protected invariants named per file (review-hardened logic, load-bearing error strings). The delegate applies per-file changes, gates after each batch, and reports per-file line deltas. Re-run every gate yourself before trusting its report; scope the round to exactly the rule subset the user picked, and have one commit per file in a stated order, simplest first, so history shows which change broke a gate.
- Refactoring code whose validation order tests pin (reject-before-build, for example) breaks tests even when each extracted helper is correct. Read the test that pins the ordering before moving any validation step.
- After a comment-deletion pass, re-run formatter and lint doc-comment rules on touched files. Deleting one line can leave an exported symbol undocumented and fail a lint that passed before. A small follow-up commit restoring the doc line is expected, not a mistake (for example, a doc-comment linter such as Go `revive`).

## Minimal change

- Make the smallest readable diff that solves the request.
- Reuse code that already exists before you write new code.
- Do not add interfaces, factories, layers, files, or dependencies the task does not need.
- Prefer explicit control flow over clever, compressed code.

## Local style

- Follow the patterns already in the file and the repository.
- Use the project's formatters, linters, and tests.

## Visibility

- Start each symbol at the tightest visibility the task allows (private, unexported, or module-internal). Widen only when a caller outside that boundary needs it.
- Export for real outside callers, not for possible future use.

## Conflict order

When rules conflict: safety first, then local consistency, then this skill, then minimal change. This skill outranks laziness or YAGNI-only shortcuts when those would break a rule here.

## Guards and gates: honest work only (user rule)

Rules are language-agnostic; tool names in the examples are Go instances of the class.

Never work around a guard, gate, hook, or check: fix the work the gate rejects.

- Never delete, skip, weaken, or comment out a test to make a suite pass. A test failing because the world changed gets updated to the new correct expectation, with the reason recorded.
- Never turn off a lint rule, remove a linter from config, or narrow a check's scope so the violation stops being reported.
- Never silence a gate with a suppression marker (`nolint`, `@ts-ignore`, `# noqa`, `#[allow]`, or your language's equivalent). Real problem: fix the code. False positive: fix the code so the tool agrees, or raise the config change as an explicit recorded decision.
- Never bypass hooks (`--no-verify`, `HUSKY=0`, a disabled CI step) or restructure a command so a gate does not run.
- A red gate is information: report the exact output, fix the root cause, re-run.
- A guard that blocks legitimate work goes to the user as a decision with evidence. Never neutralize it on your own.
- Complexity lint on table subtests: split each case into its own top-level test function (Go: a `t.Run` case becomes `TestX_SubtestName`). Restructure at the moment you would have typed the suppression marker.
- Calibration exclusions live in linter config as explicit recorded decisions, never drive-bys. Scope them (test-file path filter, specific linter, exact message text), comment why the signature is fixed, and verify with one lint run that the exclusion matches.

## File structure

Order top-level declarations like this when the language allows it (adapt only where the idiom requires):

1. Imports
2. Constants
3. Variables
4. Structs or classes
5. Constructors
6. Methods

Within a category, rank placement (stronger wins):

1. **Call order:** caller above callee. The file reads top to bottom in invocation order.
2. **Public before private** at that level: only when call order does not already place the symbols. This does not justify exporting more (see Visibility).
3. **Newer toward bottom:** when call order still does not decide, put newer code toward the bottom of the file or section.

## Unit tests: black box, given/when/then, no mocks (user rule)

- Test through the public API only. Test private helpers only when the user explicitly asks. A private function that seems to need direct testing is a design signal: either a public entry point already covers it, or it does too much.
- Every test reads as given / when / then. `given` is optional setup. `when` is mandatory: the action under test. `then` is mandatory: the asserted result. If you cannot point at the `when` or the `then`, the test is rewritten from scratch, not patched. Carry the structure through the code's design when possible; keep the phase-marker comments (see Comments).
- Avoid mocks: test real behavior. A unit test that needs a mock is usually an integration test in disguise: rewrite it against the real collaborator. Mocks stay only for what a unit test cannot run at all (network, clock, randomness, hardware), and stay thin.
