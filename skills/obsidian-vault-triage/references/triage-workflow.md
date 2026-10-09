# Triage workflow (full procedure)

Load this file before running the first batch. Batches are small on purpose:
one domain per batch, one commit per batch, verifiable progress at every step.

## Phase 0: survey and backup (once per vault)

1. Inventory the vault before touching anything:
   - file counts per top-level folder, all files plus `.md` separately
   - attachment/resource dirs and their link style (wikilink vs relative md)
   - sync markers (`.stfolder`), conflict files, empty dirs, cache dirs
   - sample-read 3-5 notes per source to understand content domains
2. Persist the inventory (in the snapshot commit message or a scratch note).
   The per-batch loss audit needs the starting counts as its denominator.
3. Propose the domain list to the vault owner before creating folders.
   Domains come from actual content, not from the source apps.
4. Backup. The `.gitignore` excludes only regenerable caches; everything else
   including `.trash/` and conflict files gets committed, because Phase 2
   edits those files and git must be able to recover their original content.
   ```bash
   cd <vault-root>
   git init
   printf '.smart-env/\n.obsidian/workspace*.json\n' > .gitignore
   git add -A && git commit -m "snapshot: pre-triage full backup"
   ```
   Attachment-heavy vaults: commit everything anyway. The safety net is the
   point; large binaries are acceptable in a private repo.

## Phase 1: batches

One batch is one domain: read, classify, write, fix links, update MOC, commit.

For each note in the batch source:

1. **Read the whole note.** Understand what it is before deciding where it
   goes. A filename like `Untitled Note.345` or a timestamp tells you nothing;
   the body might be a license key, a diary line, or a project plan.
2. **Classify** into exactly one target:
   - a domain folder note (gets a proper Title Case filename)
   - a split-source: the note contains several unrelated items, go to step 3
   - `90 Archive/` (stale, junk, obsolete) — still kept, still tagged
   After renaming, check for duplicate basenames vault-wide
   (`find . -name '*.md' -printf '%f\n' | sort | uniq -d`): wikilinks resolve
   by basename, so two notes with the same name silently break resolution.
   Disambiguate before commit.
3. **Split multi-topic notes.** A daily note or capture note often holds many
   unrelated fragments (a log excerpt, a tool discovery, a personal thought).
   Each fragment becomes its own atomic note:
   - one idea per file, Title Case filename that describes the content
   - add frontmatter: `created: <original note date>`, `tags: [<domain>/<type>]`
   - keep the original wording. Triage reorganizes, it does not rewrite.
   - the source daily note, once fully split, is removed in the same commit
     ONLY if every fragment is verifiably present in the new notes. Count
     fragments before and after; if in doubt, move it to the daily archive
     instead of deleting.
4. **Fix all links after every move.** Moving files with shell/git does not
   update any link (only moving inside the Obsidian app rewrites them).
   After each batch, sweep every link form in every moved note:
   - `[[wikilink]]` resolves by filename and survives moves, but breaks if
     the target is renamed. Renaming a note means updating inbound wikilinks.
   - `[[note|alias]]` and `[[note#heading]]` follow the same filename rule.
   - Quoted wikilinks in frontmatter (`related: "[[Note]]"`) follow the same
     rule and are easy to miss in a grep for `[[`.
   - Relative markdown links and embeds (`[t](../x.md)`,
     `![](../../_resources/hash.png)`) are path-based and break on every move.
     Recompute each path from the note's new location. Script this over all
     moved files; hand-edits miss files.
   - Absolute paths and `file://` links: rewrite to vault-relative paths or
     wikilinks. Absolute paths die on any reorganization.
   Then verify: run a broken-link scan vault-wide (grep all `[[ ]]` and `]( )`
   targets, check each resolves to an existing file) and require zero broken
   links before the batch commit. A batch is not done while a link is broken.
5. **Tag existing notes** in the same pass: minimal flat frontmatter
   (`created`, `tags`), namespaced tags `domain/type`, English namespaces.
   Do not retrofit frontmatter onto Archive in bulk, only when touching a file.
6. **Update the domain MOC**: add every new or moved note as a `[[wikilink]]`
   grouped under a heading, with a one-line description where the title
   doesn't speak for itself. Update `Home.md` if a new domain MOC was born.
7. **Commit the batch** with a message naming the domain and counts:
   `triage: joplin → 10 Dev (62 notes, 4 splits, links fixed)`. The counts
   make the diff reviewable; the loss audit below does the verification.

## Loss audit (run at the end of every batch)

```bash
# before batch (also all-files variant: -type f, excluding .git and caches)
find <sources> -name '*.md' | wc -l
# after batch
find <vault> -name '*.md' | wc -l   # must be >= before (splits add files)
git diff --stat HEAD~1              # no deletions without a matching split
```

Audit attachments too, not only `.md`: embeds and `_sources/` moves are the
files most likely to vanish. A dropped count with no split commit means lost
information. Roll back and redo the batch:
`git reset --hard HEAD~1` (or `git checkout HEAD~1 -- <paths>` for a partial
recovery), then fix the procedure gap before retrying.

## Phase 2: cleanup

- Conflict files: diff against the original, merge unique lines, delete the
  duplicate. The pre-triage snapshot still holds the originals if the merge
  misses something.
- Empty dirs and zero-note import skeletons: remove after confirming empty.
- Import resource dirs that still hold referenced attachments stay under
  `_sources/<origin>/`. Deleting them breaks links; remove only after
  re-pointing every link and verifying.
- Re-index plugin caches (embeddings etc.) after the final batch.
- Final commit: `triage: complete — <N> notes, <M> splits, audit clean`.

## Maintenance mode

New daily notes accumulate in root. Run a triage batch when they pile up;
sporadic is fine. Every pass follows the batch procedure above, starting at
the read step.

## Domain MOC conventions

- One MOC per domain folder, named `<Domain> MOC.md`, living inside the folder.
- MOC body: grouped `[[wikilinks]]` plus one-line context per group. A MOC is
  a note, not a category. Notes stay in place; the map points at them.
- `Home.md` links only to MOCs (and maybe 2-3 key notes), never to everything.
- A reader going `Home.md` → one MOC → target note should find any note in at
  most 3 hops; if a hop is missing, the next triage batch adds it.
