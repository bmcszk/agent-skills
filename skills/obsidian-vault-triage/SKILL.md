---
name: obsidian-vault-triage
description: Triage, reorganize, and maintain an Obsidian vault — lossless migration, note splitting, tagging, MOC navigation.
license: MIT
metadata:
  category: knowledge-management
---

# Obsidian Vault Triage

Triage a messy or imported Obsidian vault into a domain-organized structure
with MOC navigation, without losing a single note or piece of information.
Use when reorganizing a vault, migrating imports (Evernote/Joplin/Simplenote/Keep),
splitting daily notes into atomic notes, or tagging back-catalog notes.

## Hard rules (user requirements, non-negotiable)

1. **Read before you classify.** Every note must be read and understood before
   it is categorized. Never file by filename or origin folder alone.
2. **Zero loss.** No note, attachment, or piece of information may disappear.
   Content that looks like junk gets an `archive/` home, not deletion.
3. **Backup before triage.** Full snapshot before any write: `git init` in the
   vault root, commit everything (including a `.gitignore` that excludes only
   `.obsidian/workspace.json` and cache dirs like `.smart-env/`). One commit per
   batch = instant rollback and a readable progress log.

## Target structure

```
Home.md              # root MOC: links to all domain MOCs, always current
00 Inbox/            # unprocessed captures awaiting triage
10 <Domain>/…        # numbered domain folders (see references/structure.md)
90 Archive/          # stale/junk — kept, never deleted
_sources/<origin>/   # import resources (e.g. Joplin _resources) stay here
```

- Numbered prefixes sort naturally in the sidebar; systems near 00, archive near 90.
- Organization is thematic/domain, NOT by source app — the origin (evernote/,
  joplin/, simplenote/) is an import artifact and dissolves during triage.
- Daily notes live at vault root while active; a triage pass splits them into
  domain notes and then the daily file is emptied or moved to an archive of
  dailies. Never let processed dailies accumulate in root.

## Workflow (batch per domain)

Work in batches: one domain (or one import folder) per batch, one commit per
batch. Never attempt a whole-vault move in one pass. The full procedure,
including the note-splitting rules and MOC maintenance, is in
[references/triage-workflow.md](references/triage-workflow.md) — load it
before the first batch.

Domain naming: use the vault owner's language for folder names; use short
English tag namespaces (`dev/`, `ai/`, `home/`) for `tags:` in frontmatter.

## Vault-specific hazards (check before any move)

- **Moving with shell/git never rewrites links** — only renaming/moving inside
  the Obsidian app auto-updates them. External moves require a scripted link
  sweep covering wikilinks (including aliased, heading, and frontmatter-quoted
  forms), relative markdown links, embeds, and absolute/file:// paths, plus a
  vault-wide broken-link scan before the batch commit. See step 4 in
  references/triage-workflow.md.

- **Wikilinks survive moves** — `[[Note]]` resolves by filename, not path.
  Relative markdown links (`![](../../_resources/hash.png)`) do NOT: after
  moving a note, recompute and fix every relative path (script it, don't hand-edit).
- **Sync folders**: a folder containing `.stfolder` belongs to Syncthing —
  pause sync or exclude it before restructuring, or every peer replicates
  the churn and conflicts.
- **Conflict files** (`*.sync-conflict-*.md`): diff against the original;
  merge any unique content, then remove the duplicate.
- **Empty dirs** (`Untitled/` etc.): safe to delete once confirmed empty —
  nothing to lose.
- **Plugin indexes** (`.smart-env/` embeddings etc.): exclude from git and
  re-index after a large migration.

## After triage

Update `Home.md` and every affected domain MOC in the same batch commit.
An un-updated MOC is a broken map — worse than no map.
