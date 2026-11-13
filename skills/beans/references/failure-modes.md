# CLI failure modes

Read when a beans command reports success that later steps depend on,
when a script edits bean bodies in batch, or when a repo beans lint
fails a change that was green locally. Every failure mode here hides
behind exit 0.

- Success output is not persistence. A create can print an OK message
  and leave no file behind; a wholesale body rewrite can silently not
  take. Verify against the on-disk file (`beans show`, or grep the
  `.beans/` file for a marker line from the intended body) before
  building anything on the result.
- A status flip without its evidence in the same update passes
  locally and fails the repo lint in CI. Append the claim section
  (`## Progress log` entry naming the claiming session) in the same
  batch as the flip; only the standard evidence markers count, so a
  custom heading gets wrapped inside one.
- `--body-append` takes a single literal argument. A payload path is
  appended as a litter line (the literal path text), and an empty
  string updates nothing while still printing `Updated`. Guard
  `$(cat <file>)` payloads with `test -s`, and after every append
  grep the on-disk file for the evidence marker and for an accidental
  absolute-path line.
- `--body-replace-old` must match exactly once or the whole
  replacement fails. Lift old and new strings from a fresh read of
  the on-disk body: a string reconstructed from memory loses code
  backticks, fails `not found`, and splits a scripted batch so the
  earlier replacements land while their paired flips never run.
- Compose titled links (title as label, id only in the href) straight
  from a `.beans/` listing, never from memory: a recalled title maps
  to a wrong or nonexistent id, and a bare bracket carries no href to
  repair.
- After bulk creation, assert the on-disk file count grew by exactly
  the number created before wiring parents or blockers: a quiet
  failed create plus a blind retry equals a duplicate.
- Bean files are edited where they are committed. Copying a main
  checkout's version of an existing bean file over a branch reverts
  the branch's evidence sections and fails CI on an otherwise green
  PR: copy only new filenames, edit existing files in place, and
  hash-compare main-vs-branch before opening the PR.
- A repo beans lint that imports its parser dependency in a
  try/except silently skips every frontmatter check when the
  dependency is missing and still prints OK. Run the lint under the
  same interpreter CI uses; a bare-interpreter green is unproven.
