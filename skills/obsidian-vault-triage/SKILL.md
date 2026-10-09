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
