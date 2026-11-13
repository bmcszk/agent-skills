# CLI failure modes

Read when a beans command reports success that later steps depend on,
when a script edits bean bodies in batch, when a status flip or a PR
carries ledger changes, or when a repo beans lint fails a change that
was green locally. Every failure mode here hides behind exit 0.

## Success output is not persistence

`create` succeeding is not `create` persisting: a create can print a
usage-OK message and leave no file behind. Verify with `beans show <id>`
(or the `.beans/` listing) before building dispatches or PR bodies on
the new bean, because everything downstream then cites a bean that does
not exist. Recovery is a fresh `create` (a new id) plus a superseding
note on any bean that cited the phantom; a file is never back-filled
for an id that was never minted.

The same law covers wholesale rewrites: `beans update <id> --body-file
<f>` replaces the whole body, so after a batch, grep each target's
on-disk file for a marker line from the new body and for strings the
rewrite must have removed. An absent new marker means the update
silently did not take.

A retitle changes frontmatter only: the file keeps its original
`<prefix>-<id>--<slug>.md` name. Resolve ids by frontmatter, never by
filename slug, and expect title-to-filename drift after any retitle.

## Status flips carry evidence in the same update

`beans update <bean> -s in-progress` with an empty append flips the
status and records no claim evidence, which the repo beans lint rejects
once the change reaches CI. Append the claim section in the same
update: a dated line under `## Progress log` naming the claiming
session; later appends add the PR, verdict, and close-out lines. Only
the evidence markers count (`## Progress log`, `## Proof of Work`, or a
claimed timestamp line), so a custom claim heading gets wrapped inside
a `## Progress log` heading. Re-run the beans lint before building
anything on the claim.

## Appends are one literal shell argument

`--body-append` takes a single argument, so a multi-line payload
travels through a small script file with the argument inline. Guard
every `--body-append "$(cat <file>)"` with `test -s <file>` in the same
script: a staging path the script runner resolves differently silently
feeds an empty string, the update still prints `Updated`, and a status
flip riding the same invocation closes the bean with no evidence behind
it. Keep the append and the status flip in separate invocations.

The payload path itself is never the argument: `--body-append <f>`
appends the literal path text as a litter line and nothing else, which
also defeats later `--body-replace-old` matches built from the intended
body. After every append, grep the on-disk bean file for the evidence
marker and for an accidental absolute-path line; a path line means the
substitution was skipped, so replace the litter line out and re-append
properly.

## Replace anchors are unique and lifted from disk

`--body-replace-old` must match exactly once; text found twice fails
the whole replacement. Pick the real target by extending the old string
to a two-line context pair (the preceding line plus the target line),
with the new string the same pair carrying only the intended change.

Lift old and new strings from a fresh read of the on-disk body: a
string reconstructed from memory loses code backticks and markdown
wrappers, fails `not found`, and splits a scripted batch so the earlier
replacements land while their paired appends and status flips never
run. Re-read the file and repair the failed pair in the same session.

## Cross-references composed from disk

The titled-link law (title as label, id only in the href) lives in the
SKILL.md body. The failure mode to guard is recall-based composition: a
title remembered from chat maps to a wrong or nonexistent id, a
half-recalled href usually resolves to a different bean, and a bare
bracket carries no href to repair. Compose reference pairs straight
from disk before writing any payload that cites other beans: list
`.beans/` filtered per cited subject, set title and href side by side,
then write the body. Fix a bad link through
`beans update --body-replace-old/--body-replace-new`, never by
hand-editing the bean file.

## Bulk creation asserts the file count

1. Write every body to a scratch file first; keep titles short and
   non-numeric.
2. `beans create "<title>" --body-file <f> --json` per bean; capture
   the id from JSON.
3. Assert the on-disk file count in `.beans/` grew by exactly the
   number created before wiring anything downstream (the
   phantom-create guard).
4. Wire the tree with one `beans update <id> --type <t> --parent <pid>`
   per bean, then re-read each frontmatter to confirm type, status, and
   parent landed.
5. Run the repo beans lint and commit only after it exits clean.

## Bean files are committed where they are edited

`beans create` and `beans update` write `.beans/` in the current
checkout, while the ledger a PR carries must be committed on the same
branch as the work it tracks. The working pattern: create and update in
the main checkout, copy only the touched bean file into the worktree's
`.beans/`, commit it there, then restore the main checkout so it stays
clean.

Copying the main checkout's version of an existing bean file over the
branch reverts it: the branch is usually ahead for beans it enriched
with evidence sections, and the copy makes CI fail the completion
evidence check on an otherwise green PR. Copy only new filenames; touch
existing files through a targeted edit in the worktree. Before opening
or pushing a PR, hash-compare every changed bean file main-vs-worktree;
the drift set is the authoritative sync set, and the beans lint re-runs
inside the worktree after syncing.

## A lint without its parser prints a false OK

A repo beans lint that imports its parser dependency in a try/except
silently skips every frontmatter-dependent check when the dependency is
missing, and still prints `OK`. Local green is meaningless unless the
lint runs under an interpreter that has the dependency; CI always has
it, so run the same interpreter locally that CI uses, and treat a
local green from a bare interpreter as unproven.
