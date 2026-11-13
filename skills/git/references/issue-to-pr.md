# Issue to PR: premise validation

Read when turning a tracker issue or bug report into a code change.
The failure mode this file prevents: implementing the report as
written when the report's premise is stale, duplicated, or already
solved, and shipping a PR for a problem the current code does not
have.

## Read the full thread before implementing

Read every comment on the issue, including the ones after the
original post: a later comment often narrows, corrects, or retracts
the premise, and implementing the opening post ships the retracted
version. Reproduction steps written against an older version can
describe behavior the current code already fixed.

## Sweep duplicates with synonym variants

Search the tracker before writing a line, and search with synonym
variants of the report's wording ("crash", "panic", "segfault";
"slow", "hang", "freeze"): duplicates filed under different words are
the common case, and the duplicate thread usually carries the
stronger diagnosis or the already-open fix branch.

## Recover prior design intent from history

`git log -S "<key symbol>"` finds the commits that introduced or
removed the symbol the issue touches. A "missing" behavior that
history shows was deliberately removed is a design decision to
re-litigate in the issue, not a bug to silently reintroduce.

## Validate the premise against current code

Reproduce or refute the claim against the current tree before
writing a line: run the reported path, read the code that owns it,
and state in the PR body which premise held. An issue can be valid
while its proposed fix targets the wrong layer; validating the
premise, not the proposal, is what the first commit encodes.
