# Context pointers: wording decides triggering

A skill body loads only on match, so files a run may need must be
reachable through the wording of the pointer to them. The pointer's
wording, not the target's content, decides whether the run reads it.

## Pointer wording rules

- Name the load condition in the pointing sentence, in the reader's
  task words: "when the run times out, read references/eval-patterns.md".
  A bare path with no condition never fires.
- Point forward with the trigger, not backward with the history: "when
  X happens, read Y", not "Y was written because of X".
- One pointer, one condition. A pointer listing three conditions
  reads as marketing and fires for none of them.
- The pointer sentence carries the consequence of skipping: "when the
  loop stalls, read references/recovery.md before retrying" beats a
  neutral "see also".

## Two loads, one budget

Every token costs the same whether it teaches the current task or
distracts from it, but the two loads differ:

- Context load: tokens occupying the window right now, whatever they
  say.
- Cognitive load: how much of that text the reader must process to
  act.

A body can be long and still cheap if every line is live for the
current task; a short body full of dead sections is expensive.
Progressive disclosure is the budget mechanism: the body carries
laws, references carry procedures, and the pointer wording moves
tokens from context load to on-demand load.

## In-file steps vs referenced files

- Steps that must run in order stay in the body: a run following a
  procedure should not hop files mid-sequence.
- Reference material a run reads at one decision point lives in a
  file behind a condition-named pointer.
- A reference the body never points to is dead weight; a body
  pointing at a missing file dead-ends the run. Both fail review.
