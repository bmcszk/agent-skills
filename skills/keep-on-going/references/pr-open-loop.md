# PR-open loop

The body carries the law (a PR awaiting review is not a stopping
point). This reference is the loop a run follows while the PR is
open.

1. **Run a retrospective audit** on the session so far: audit the
   problems actually hit (wrong model dispatches, stalled RPC lanes,
   narration comments, scope-rule misses), fix their structural
   causes in the governing skills, contracts, or hooks. Lessons land
   where the next session loads them, not in chat history.
2. **Continue the epic loop** on the same branch: next ready bean,
   re-gate, commit, push. The open PR absorbs the new commits.
3. **Frontier check**: a genuine human decision that surfaced
   mid-wave gets batched into one focused question-list session
   (whole frontier, numbered, recommended answers). Ad-hoc asks and
   waiting are both failures.

Communication: report state in one line ("PR open, worker on X,
next Y"), never end a turn with idle capacity while beans are ready.

Session close needs a LEDGER-shaped state summary, not narrative:
beans closed (by title, not id), commits pushed, CI verdict, next
pick. The next session loads the ledger, not the transcript.

## Retro loopback

Every retro finding gets a **structural** fix, never a verbal one:

- a mistake a check could catch: wire the check (linter rule, CI job,
  pre-push hook) before writing any prose rule;
- a wrong dispatch pattern (model choice, contract shape): fix the
  delegating skill's contract template so the next dispatch inherits
  the fix;
- a steering rule that failed: patch the skill that owns it, not the
  session transcript.

Retro closes only when the problems that already occurred cannot
recur through the same path.
