# Skill harvest: harvesting local mutations

The global skill dir (`~/.agents/skills`) mutates constantly: working
sessions amend installed skills in place (edits, lesson writes,
quick fixes). Any `skills update` or reinstall overwrites those local
changes. Management = harvest the valuable ones upstream before they die.
Load this when a skill diverges from its upstream repo, before bulk
updates, or when the user reports local skill edits.

## The loop

1. **Detect drift.** Hash-compare installed vs upstream per file
   (skill-craft's [references/repo-maintenance.md](repo-maintenance.md) has the diff recipe). Diffs are
   candidates; style-only churn (em dash rewrites, hash timestamps) is
   not.
2. **Triage each change** - three questions, all must answer yes:
   - Does it carry valuable knowledge (a fix, a law, a failure mode that
     cost real time)?
   - Is it worth pushing upstream (would a fresh install of the skill
     be worse without it)?
   - Is it project agnostic (no repo names, paths, creds, one-off
     project jargon)?
3. **Move yeses upstream.** Copy the changed content into the source
   repo, branch, PR - the changes follow the full skill-craft rulebook
   (token budget, verify commands, description routing) plus unslop
   (no AI tells, no em dashes) and ponytail (smallest complete change;
   drop restated prose to pay for the new lines).
   - Re-read the installed copy section by section for contamination
     before copying: a session may have written genuine laws AND
     project-specific debris (lane names, worker plumbing, one-off
     status rules) into the same file. Debris passes the three triage
     questions on a file-level skim because it reads polished - judge
     each section; rewrite project-flavored phrasing tool-agnostic or
     drop it.
   - Do not add scope-exclusion paragraphs: a section listing what the
     skill does NOT cover documents nothing actionable - the
     description already routes tasks in and out. User law: out-of-scope
     notes are bloat.
   - A contract quoting a markdown deliverable that carries its own
     triple-backtick fences anchors the block end explicitly
     (insert-before anchor lines), and the parent's fidelity check
     searches for the closing fence from the opener onward: a
     from-position-zero search matches the opener itself and fakes a
     mismatch. A failed extraction means the extractor first; only a
     clean pass accuses the worker.
   - Treat the consuming repo's own review gates as binding: a repo
     that ships a vendor-agnosticism rule gets the delta checked
     against it before commit.
4. **Say no cleanly.** Not valuable / not agnostic = leave local, expect
   overwrite on update, and note that in the PR or session log. A local
   change kept local is disposable by design - that is fine, not loss.

## Order of operations (never lose work)

Harvest BEFORE running any `skills update` / reinstall: update first
means the local mutations are gone and there is nothing to triage. If
update already ran, recover from git history of the source repo, session
logs, or the other session's transcript - do not rewrite from memory.

## Multi-source note

Installed skills come from several upstreams (own repo, third-party
imports). Only skills whose source repo accepts PRs from this user are
harvestable; third-party skills get wrapper amendments instead
(personal-skill-authoring law), never upstream PRs.
