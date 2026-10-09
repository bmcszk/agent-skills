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
