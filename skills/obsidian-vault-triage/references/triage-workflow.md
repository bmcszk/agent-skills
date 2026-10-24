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
   When dumping bodies by splitting on `---`, check for block scalars in
   frontmatter (`frontmatter: >-`, `tags: |-`): an importer that wrapped the
   body inside frontmatter makes a naive split read the note as empty or
   tag-only. A frontmatter block hundreds of lines long is the tell - read
   the raw file before writing the verdict. `titlecheck.py` flags these
   (exit 1) - treat the flag as "raw read required", and after unwrapping a
   wrapped note audit WORD-LEVEL (old vs new, not line-level: the fold
   changes line breaks) that nothing was dropped before committing.
2. **Classify** into exactly one target:
   - a domain folder note (gets a proper Title Case filename)
   - a split-source: the note contains several unrelated items, go to step 3
   - `90 Archive/` (stale, junk, obsolete), still kept, still tagged
   After renaming, check for duplicate basenames vault-wide
   (`find . -name '*.md' -printf '%f\n' | sort | uniq -d`): wikilinks resolve
   by basename, so two notes with the same name silently break resolution.
   Disambiguate before commit.
3. **Split multi-topic notes.** A daily note or capture note often holds many
   unrelated fragments (a log excerpt, a tool discovery, a personal thought).
   Split ONLY at top-level topic boundaries: a new item starts at a top-level
   heading of a distinct subject, not at every `##`. Sub-headings like
   `Summary`, `Key Points`, `Products`, `Notes`, `Zakres usług` are SECTIONS
   of their parent item, not separate notes - they must stay glued to the
   parent. An orphan section-note (`2026-08-25 - Summary.md`) is contextless
   garbage and a triage failure; when in doubt, merge. Each remaining topic
   becomes its own atomic note:
   - one idea per file, Title Case filename that describes the CONTENT.
     Never keep generic section words as titles; retitle from the body
     ("CRUD Events vs Business Events", not "Summary").
   - filenames cannot contain `/`: titles like `r/subreddit` or `A/B` must be
     normalized (`r-subreddit`, `A-B`) in the FILENAME and every MOC link,
     or the link silently breaks.
   - add frontmatter: `created: <original note date>`, `tags: [<domain>/<type>]`
   - keep the original wording. Triage reorganizes, it does not rewrite.
   - classify by READING each topic. Never batch-classify with a keyword
     regex over the body: substring matching misfiles relentlessly
     ("vat" inside "private", "dom" inside random English words). A regex
     over 100 notes is exactly the "read the filename" mistake at scale.
   - before removing the source, verify COVERAGE AT LINE LEVEL: every
     non-trivial content line of the source (whitespace-normalized) must
     appear in the new notes, and every source topic must map to exactly one
     destination (no double-filing, none uncovered). A file count alone
     cannot catch a merged or shredded note. Two blind spots:
     (a) MOVE+MERGE of near-duplicate notes into one destination - verify
     each source's content lines appear verbatim in its OWN destination, not
     just anywhere in the corpus, and prove suspected duplicates with a
     word-subset check before folding (keep each generation as a section,
     don't drop "the shorter one").
     (b) original frontmatter tags: preserve them verbatim in the merged
     note - the audit is mechanical and flags a dropped tag line as lost
     content even when a synonymous tag exists.
   - the source daily note, once fully split, is removed in the same commit
     ONLY if that line-level coverage check passes; if in doubt, move the
     source to the daily archive instead of deleting.
   - MOC pruning after a move: match stale links by the OLD basenames from
     the move log (the retitle changed them), never by new titles. Script
     this with the mapping JSON; a hand-prune keyed on the wrong side
     silently removes nothing.
   - When executing a move plan, skip the delete when source and destination
     resolve to the same path (`os.path.abspath(sp) == os.path.abspath(dp)`):
     write-then-remove on the same path deletes the note you just wrote. The
     damage is silent until coverage_audit reports `destination missing` and
     linkcheck counts climb - recover verbatim from git HEAD, never re-type.
   - When consolidating a theme that lives in many domains (e.g. all poetry,
     all receipts), build the candidate set from tags AND every MOC/wiki
     reference, then READ each candidate's body before the verdict - a
     `poetry` tag can sit on a prose story or a band list, and an article
     ABOUT poetry is not poetry. Keep multi-variant texts as separate notes
     (draft vs full version) unless word-subset proves one contains the
     other; retitle from the first verse line when the filename is a
     timestamp or `Untitled`.
   - Flagged misfiles travel in packs. One misfiled note means a whole
     import-era batch was classified by tags or filename: after fixing the
     flagged note, sweep its original source folder (recover the batch list
     from the snapshot commit) and re-read every sibling before declaring
     the report fixed. The flagged note names the CLASS of error (a vet
     clinic in Dev, a nickname list in Dev, car DTC reports in Dev) - read
     the domain and evict every note sharing the cause, not just the one
     named.
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

After commit, diff each moved note against its pre-move version
(`git show HEAD~1:<old-path>` vs the new file): expect byte-identical, or
frontmatter-only additions. Any body diff is a problem - this audit is what
lets the user trust "I only moved them, nothing changed".

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
- Final commit: `triage: complete - <N> notes, <M> splits, audit clean`.

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
