# Closure gates contract

Read when closing any bean (`beans update -s completed`) or when a
closure was rejected. The body carries the two binding rules; this
file carries the worked contract: exact section shapes, commands,
and the type-specific proof table.

## Rule 1: task and subtask closure

A task or subtask cannot close without a `## Proof of Work` section
in its body. The section is the evidence the verify gate ran,
separate from `## Summary of Changes` (which records what changed).
It must contain, at minimum:

- The exact commands run (build, test, lint, smoke check -
  whatever applies).
- The observed result for each command (exit status, key signal:
  counts, pass/fail, output fingerprint).
- Type-specific proof, in addition to the project's own gates:
  - `task` / `subtask`: at least one working unit test covering the
    behavior the bean changed, shown with its pass output.
  - `feature`: a working integration or e2e test covering the use
    cases (BDD style - scenarios in Given/When/Then naming or
    structure), shown with its pass output.
- A `Residual:` line - named leftovers, or `none`.

If `## Proof of Work` is missing, the closure is rejected. Append it
first, then mark completed:

```bash
beans update myproj-a3x1 --body-append "## Proof of Work
<build>    → exit 0
<test>     → PASS (148s)

Residual: none."
beans update myproj-a3x1 -s completed
```

Placeholders stand for the project's own entry points; an example
never presumes a stack. The verify gate itself stays binding: red
gate = fix the root cause; cannot verify = leave `in-progress`.

## Rule 2: epic closure

An epic cannot be closed while any of its tasks or subtasks are
still open, and cannot be closed without full end-to-end tests plus
`## Proof of Work`. Two-part gate:

- **No open children.** Every task and subtask under the epic must
  be `completed` or `scrapped` before the epic itself can move to
  `completed`. Check with:

  ```bash
  # Find any non-terminal child of the epic
  beans list --json --parent myproj-epic --no-status completed --no-status scrapped
  # Empty output → safe to close the epic.
  ```

- **Full end-to-end tests + `## Proof of Work`.** The epic's proof
  is integration-level: evidence the goal as a whole was reached
  end-to-end. Append a `## Proof of Work` section whose commands
  cover:

  - The full test suite (unit + integration + e2e, where they
    exist).
  - End-to-end / smoke checks that exercise the goal as a user
    would (browser, CLI invocation, API roundtrip, etc.).
  - For build/deploy epics, the live artifact and its reachable URL
    or version.

A goal that says "ships feature X" without exercising X end-to-end
is not proven. No e2e harness exists? Say so under `Residual:` with
the reason - silent omission is a violation.
