# Test-first theory: seams and anti-patterns

The TDD law lives in the SKILL.md body (red-green, always). This
reference is the part that makes the loop produce tests worth
keeping: where tests attach, what a good test is, and the three
anti-patterns that quietly ruin suites.

## Seams: where tests go

A seam is the public boundary you test at: the interface where you
observe behavior without reaching inside. Tests live at seams, never
against internals.

Test only at pre-agreed seams. Before writing any test, write down
the seams under test and confirm them with the user. You cannot test
everything, so agreeing seams up front is how testing effort lands on
critical paths and complex logic instead of spreading across every
edge case. Give each proposed seam a one-line note on what it catches
and what it misses.

## What a good test is

Tests verify behavior through public interfaces, not implementation
details. Code can change entirely; tests should not. A good test
reads like a specification: a sentence naming a capability that
survives refactors because it ignores internal structure.

## Anti-patterns

- Implementation-coupled: mocks internal collaborators, tests private
  methods, or verifies through a side channel (querying the database
  instead of using the interface). The tell: the test breaks when you
  refactor but behavior has not changed.
- Tautological: the assertion recomputes the expected value the way
  the code does, so it passes by construction and can never disagree
  with the code. Expected values come from an independent source of
  truth: a known-good literal, a worked example, the spec.
- Horizontal slicing: writing all tests first, then all
  implementation. Bulk tests verify imagined behavior: they test the
  shape of things rather than user-facing behavior, go insensitive to
  real changes, and lock in test structure before the implementation
  is understood. Work in vertical slices instead: one test, one
  implementation, repeat, each cycle a tracer bullet that responds to
  what the last one taught.

## Rules of the loop

- Red before green: write the failing test first, then only enough
  code to pass it. No speculative features.
- One slice at a time: one seam, one test, one minimal implementation
  per cycle.
- Refactoring is not part of the loop: it belongs to the review
  stage, after the slice is green.

## Phase markers in practice

The SKILL.md Comments section makes the `given` / `when` / `then`
markers required structure; the non-obvious placement rules:

- A marker owns the statements below it up to the next marker, so a
  marker with no code beneath it is decoration: a dangling `// given`
  is deleted, optional setup earns no empty marker.
- One test, one act: `when` holds the single act under test, `then`
  only observes. A second unit call inside `then` is a missing test,
  not a placement problem. A repeated act under parametrization is
  still one act.
- Table-driven loops carry no marker scope of their own: drive all
  rows through one top-level act under a single `// when` / `// then`
  pair, with per-row expectations as row fields.
- A fluent DSL whose phases are receivers in a chain carries no
  marker comments: the chain is the structure, and markers on top
  build a competing one.
- The phase name is the line's first word (`// if x then y` is prose,
  not a marker), and in Go a marker inside a `t.Run` closure
  satisfies that subtest while leaving the enclosing test unmarked.
