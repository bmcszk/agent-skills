# Triage Workflow (full procedure)

Load this file before running the first batch. Batches are small on purpose:
one domain per batch, one commit per batch, verifiable progress at every step.

## Phase 0 — Survey and backup (once per vault)

1. Inventory the vault before touching anything:
   - file counts per top-level folder (`find <dir> -name '*.md' | wc -l`)
   - attachment/resource dirs and their link style (wikilink vs relative md)
   - sync markers (`.stfolder`), conflict files, empty dirs, cache dirs
   - sample-read 3-5 notes per source to understand content domains
2. Propose the domain list to the vault owner before creating folders.
   Domains come from actual content, not from the source apps.
3. Backup:
   ```bash
   cd <vault-root>
   git init
   printf '.smart-env/\n.trash/\n.obsidian/workspace*.json\n*.sync-conflict-*\n' > .gitignore
   git add -A && git commit -m "snapshot: pre-triage full backup"
   ```
   Attachment-heavy vaults: commit everything anyway — the safety net is the
   point. Large binaries are acceptable in a private repo.

## Phase 1 — Batches

One batch = one domain = read → classify → write → MOC → commit.

For each note in the batch source:

1. **Read the whole note.** Understand what it is before deciding where it
   goes. A filename like `Untitled Note.345` or a timestamp tells you nothing;
   the body might be a license key, a diary line, or a project plan.
2. **Classify** into exactly one target:
   - a domain folder note (gets a proper Title Case filename)
   - a split-source: the note contains several unrelated items → go to step 3
   - `90 Archive/` (stale, junk, obsolete) — still kept, still tagged
3. **Split multi-topic notes.** A daily note or capture note often holds many
   unrelated fragments (a log excerpt, a tool discovery, a personal thought).
   Each fragment becomes its own atomic note:
   - one idea per file, Title Case filename that describes the content
   - add frontmatter: `created: <original note date>`, `tags: [<domain>/<type>]`
   - keep the original wording — triage reorganizes, it does not rewrite
   - the source daily note, once fully split, moves out of root (archive of
     dailies) or is deleted in the same commit ONLY if every fragment is
     verifiably present in the new notes — count fragments before and after.
4. **Fix links after moves.**
   - `[[wikilinks]]` need nothing — they resolve by filename vault-wide.
   - Relative markdown links/images: after moving a note, recompute each
     relative path to the resource. Do this with a script over all moved files
     in the batch; hand-edits miss files. Verify a sample of image links
     resolves after every batch that moved resource-linked notes.
   - If two notes share a filename across folders, wikilinks silently resolve
     to the alphabetically-first path — rename one of the duplicates.
5. **Tag existing notes** in the same pass: minimal flat frontmatter
   (`created`, `tags`), namespaced tags `domain/type`, English namespaces.
   Do not retrofit frontmatter onto Archive in bulk — only when touching a file.
6. **Update the domain MOC**: add every new/moved note as a `[[wikilink]]`
   grouped under a heading, with a one-line description where the title
   doesn't speak for itself. Update `Home.md` if a new domain MOC was born.
7. **Commit the batch** with a message naming the domain and counts:
   `triage: joplin → 10 Dev (62 notes, 4 splits, links fixed)`.
   The count in the message is the loss audit — the sum of committed notes
   must equal the inventory from Phase 0 minus notes still pending.

## Loss audit (run at the end of every batch)

```bash
# before batch
find <sources> -name '*.md' | wc -l
# after batch
find <vault> -name '*.md' | wc -l   # must be >= before (splits add files)
git diff --stat HEAD~1              # no deletions without a matching split
```

A dropped count with no split commit = lost information. Stop and recover
from the snapshot before continuing.

## Phase 2 — Cleanup

- Conflict files: diff vs original, merge unique lines, delete duplicate.
- Empty dirs and zero-note import skeletons: remove after confirming empty.
- Import resource dirs that still hold referenced attachments stay under
  `_sources/<origin>/` — deleting them breaks links; only remove after
  re-pointing every link and verifying.
- Re-index plugin caches (embeddings etc.) after the final batch.
- Final commit: `triage: complete — <N> notes, <M> splits, audit clean`.

## Maintenance mode (ongoing)

- New daily notes accumulate in root; run a triage batch when they pile up
  (sporadic is fine — the process, not the frequency, prevents rot).
- Every triage pass follows the same batch procedure above, starting at the
  read step. The vault stays honest because every batch ends committed and
  audited, not because it happens often.

## Domain MOC conventions

- One MOC per domain folder, named `<Domain> MOC.md`, living inside the folder.
- MOC body: grouped `[[wikilinks]]` + one-line context per group. A MOC is a
  note, not a category — notes stay in place, the map points at them.
- `Home.md` links only to MOCs (and maybe 2-3 key notes), never to everything.
- An agent or human reading `Home.md` → one MOC → target note should find any
  note in ≤3 hops; if a hop is missing, the next triage batch adds it.
