# Leaf Work — Four Passes on One Bean

The per-bean recipe. Use this after `beans update <id> -s in-progress`
and before `-s completed`. The parent `SKILL.md` defines when to
loop; this file defines how to do one loop iteration well.

## Pass 1 — Implement the complete deliverable

Do the whole job. No placeholders. No "TODO later". No deferred
remainder. If the body says "implement X", X ships in this pass.

This is the only pass where you write code. The next three passes are
about making that code honest.

## Pass 2 — Re-read as a domain expert

Pretend you didn't write it. Read the diff as if someone else
committed it and you are reviewing their PR. Replace the cheap
version of each part:

- The naming choices.
- The error handling.
- The boundary cases.
- The unnecessary work.

If a part has a "because the spec says so" justification, ask whether
the spec is right. If a part has a "this is what I always do"
justification, ask whether "always" still applies.

## Pass 3 — Hunt defects

Five classes. For each, ask: "what's the obvious thing I broke?"

- **Correctness.** Does it do what the bean says? Does it do it on
  every input, including weird ones?
- **Integration.** Does it interact correctly with the code it
  touches — callers, callees, the build, the test harness, the
  runtime, the network, the schema?
- **Portability.** Does it work on the platforms the project claims to
  support? On the CI runner? On a fresh checkout?
- **Performance.** Is there an O(n²) where O(n) is one line away? A
  quadratic loop hiding in the happy path? An allocation in a hot
  loop? An N+1 query?
- **Evidence.** Will the verify gate actually catch a regression? Is
  the test running the right surface? Is the assertion checking the
  right invariant?

Fix what you find. If you find a defect outside the scope of the
bean, leave a comment and decide whether to spawn a follow-up bean
(not a silent expansion of the current one).

## Pass 4 — Polish, then repeat

Low-cost polish:

- Trailing whitespace, odd imports, dead dead code.
- Inconsistent naming.
- Comment that explains *why*, not *what*.
- Doc comments on exported symbols.
- Changelog / commit message that names the bean ID.

Then **go back to pass 2**. Repeat until a full pass from 2 finds
nothing new. Stop when 4 successive passes are no-ops.

## Finish

A leaf is finished only when:

- All four passes are clean.
- The verify gate ran and passed (recorded in `## Proof of Work`).
- Every acceptance criterion in the body is `- [x]`.
- The bean can be closed without surprising the user on review.

A leaf that hits an impossible gate (something you can't prove at
all in this environment) is **not finished** — it's handed off.
See [`approvals.md`](approvals.md) for how to record an impossible
gate and scrap the bean honestly.

## What this is not

- It is not a checklist you tick once. Passes 2–4 are loops.
- It is not a substitute for the project's own lint + test +
  review. Run those — they're the verify gate.
- It is not a license to expand the bean's scope. Findings that
  aren't on the bean's path are follow-up beans, not silent edits.