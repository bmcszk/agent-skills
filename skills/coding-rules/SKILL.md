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

## File structure

Order top-level declarations like this:

1. Imports
2. Constants
3. Variables
4. Structs or classes, public first
5. Constructors, public first
6. Methods, public first

Keep this order when the language allows it, and adapt only where the language idiom requires.


## Test-DSL constructors (fluent DSL, user rule)
ONE base struct `parts` holds ALL DSL state — no composite/god fixture type, no state split across domain structs, no embedding cycle (base embedding domains was rejected as circular; a wrapping fixture type was rejected as a stupid pattern). Every `*_parts_test.go` file = its OWN struct extending the base (`type <dom>Parts struct { parts }`), then a ctor returning THAT struct pointer 3×, then methods — a parts file whose ctor returns bare `*parts` reads as missing its struct. The domain ctor CONSTRUCTS the parts core inline — NEVER `return newParts(t)` delegation. Keep ALL builders on the base `*parts` returning `*parts`: promotion keeps mixed-domain chains and `.and()` intact while domain structs stay stateless markers. Do NOT add self-typed generics (`parts[S]`) to preserve chain typing — promoted methods returning `*parts` already keep chains working, while self-types break every cross-domain chain link (each link needs one concrete type). Scratch-compile the candidate topology in a throwaway module (struct + ctor + one mixed-domain chain) before touching the real corpus.

## Redesign pushback (lifecycle)
When the user rejects a delivered structure, the fix is to DELETE the rejected abstraction and return to the simplest shape, not to patch the abstraction's naming or wiring. Before restructuring a working fluent DSL at all, inventory what the current shape already guarantees (chain typing, mixed-domain access) and price the churn in chain sites — reject a redesign that trades one complaint for a thousand-site mechanical diff unless the user explicitly asked for the type model. A green gate never excuses a re-added narration comment: audit the diff for added `//` lines before reporting done.
