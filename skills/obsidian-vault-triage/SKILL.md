---
name: obsidian-vault-triage
description: Triage, reorganize, and maintain an Obsidian vault. Lossless migration, note splitting, tagging, MOC navigation.
license: MIT
metadata:
  category: knowledge-management
---

# Obsidian vault triage

Triage a messy or imported Obsidian vault into a domain-organized structure
with MOC navigation, without losing a single note or piece of information.
Use when reorganizing a vault, migrating imports (Evernote, Joplin, Simplenote,
Keep), splitting daily notes into atomic notes, or tagging back-catalog notes.

## Hard rules (user requirements, non-negotiable)

1. **Read before you classify.** Read and understand every note before
   categorizing it. Never file by filename or origin folder alone.
2. **Zero loss.** No note, attachment, or piece of information may disappear.
   Content that looks like junk gets an `archive/` home, not deletion.
3. **Backup before triage.** Full snapshot before any write: `git init` in the
   vault root, commit everything. The `.gitignore` excludes only regenerable
   caches (`.smart-env/`, `.obsidian/workspace*.json`). One commit per batch
   gives instant rollback and a readable progress log.

## Target structure

```
Home.md              # root MOC: links to all domain MOCs, always current
00 Inbox/            # unprocessed captures awaiting triage
10 <Domain>/…        # numbered domain folders (see references/structure.md)
90 Archive/          # stale/junk, kept, never deleted
_sources/<origin>/   # import resources (e.g. Joplin _resources) stay here
```

- Numbered prefixes sort naturally in the sidebar; systems near 00, archive
  near 90.
- Organization is thematic/domain, never by source app. Origin folders
  (evernote/, joplin/, simplenote/) are import artifacts: their notes get
  sorted into domains and the folders removed.
- Daily notes live at vault root while active. A triage pass splits a daily
  note into domain notes; the daily file is removed only after every fragment
  is verified present in the new notes.

## Workflow (batch per domain)

Work in batches: one domain (or one import folder) per batch, one commit per
batch. Never attempt a whole-vault move in one pass. The full procedure,
including the note-splitting rules and MOC maintenance, is in
[references/triage-workflow.md](references/triage-workflow.md). Load it before
the first batch.

Gate scripts (run from `scripts/`, do not reinvent per session):

- `linkcheck.py <vault>` — every `[[wikilink]]` and relative `](` target
  resolves. Zero broken links before a batch commit; classify each reported
  break as real or false positive (code spans, original import text) before
  touching anything.
- `titlecheck.py <vault>` — no note carries a bare section-word title
  (`Summary`, `Key Points`, `Produkty`, …). Sections stay glued to their
  parent note; an orphan section-note is a triage failure. Exit 1 = fix the
  split.
- `coverage_audit.py <vault> <mapping.json>` — run BEFORE removing a split
  source. Mapping JSON: `{"<source-relpath>": ["<dest-relpath>", …]}`. Every
  non-trivial source line must exist in the destination corpus and every
  source maps to exactly one destination. Exit 1 = lost content, stop.

A vault git repo should wire `titlecheck.py` + the staged-file linkcheck as a
`pre-commit` hook so the gates run without agent discipline. Know what the
gates CANNOT catch: wrong-domain classification (`Gabinet Weterynaryjny` in
`10 Dev/`) passes all three gates — a structurally perfect vault can still be
misfiled. Classification is guarded only by the read-per-note rule; gates
guard structure and loss. A user-flagged misfile is a CLASS signal: read the
whole source domain and refile every sibling sharing the cause (see the
workflow's "flagged misfiles travel in packs").

Keep gate docs honest: when a documented script mode (e.g. coverage_audit
reading a moved source from git HEAD) is not actually implemented, either
ship it or fix the doc — a gate that exits 1 on its documented happy path
gets worked around ad-hoc, and the workaround is where mistakes happen.

Import-era frontmatter can wrap a note's ENTIRE body in a block scalar
(`frontmatter: >-` / `tags: |-`). titlecheck flags these — the body is
invisible to a naive `---` split, so such a note reads as empty and gets
filed as an "empty stub". Never verdict a flagged note without a raw file
read, and when unwrapping, audit word-level (old vs new) before committing.
After a move batch, run the post-move verification from the workflow's loss
audit (byte-diff each moved note vs `HEAD~1:<old-path>`) — "I only moved
them" is a claim to prove, not assert.

Watch out for a Python gotcha in move loops: dumping bodies by splitting on
a regex `^---$` mis-parses notes whose BODY contains a literal `---` fence
(a separator line inside the text) — the split reads only the last chunk as
the body. For verdict-critical reads use the raw file (or a split that
requires the frontmatter to be the FIRST block).

Domain naming: use the vault owner's language for folder names; use short
English tag namespaces (`dev/`, `ai/`, `home/`) for `tags:` in frontmatter.

## Vault-specific hazards (check before any move)

- **Moving with shell/git never rewrites links.** Only moving or renaming
  inside the Obsidian app auto-updates them. External moves need the scripted
  link sweep and broken-link scan from reference step 4.
- **Sync folders**: a folder containing `.stfolder` belongs to Syncthing.
  Pause sync or exclude it before restructuring, or every peer replicates the
  churn and conflicts.

## After triage

Update `Home.md` and every affected domain MOC in the same batch commit.
Update it in the same commit or the map goes stale and misleads.
