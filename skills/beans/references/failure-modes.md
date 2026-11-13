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
- Repo linters report required-section gaps ONE AT A TIME: fixing a
  single missing heading and re-running surfaces the next gap on
  the next run, one rerun per gap. Copy the full skeleton (all
  required sections) from a lint-clean bean of the same type
  instead, and pass in one run.
- Verify a claimed fix where the CONSUMER reads the fixed value, not
  where the writer wrote it: the installed path is not the serving
  path (a repo checkout can differ from the running unit's copy).
  Resolve the unit ExecStart or `/proc/<pid>/cmdline` first to learn
  what actually executes, then verify against that copy.
- Old fix notes go stale when routing, config, or availability
  change: a note verified last month describes last month's paths.
  Re-verify before carrying the note forward into a new campaign or
  bean.
- CLI gaps that hide behind exit 0: `beans show` strips custom YAML
  fields (read the `.beans` file directly to see them);
  `--parent ''` is a silent no-op (clearing a parent is
  `--remove-parent`); `update -t` retype skips parent re-validation
  (verify parentage via `list --json` and do retype plus parent fix
  in one batch); an empty-filter `list --json` emits literal `null`
  not `[]` (guard the consumer); `list --json` can carry raw control
  chars (parse with `strict=False`); `create --json` nests the bean
  under `.bean.id`, not at the top level.
