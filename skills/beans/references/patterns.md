# Workflow Patterns

Recipes for using beans. The rules, lifecycle, and closure gates live in
the parent `SKILL.md`; this file is the **how**.

## Start work on a bean

```bash
# 1. Find what's ready (post-triage)
beans list --json --ready

# 2. Claim
beans update myproj-a3x1 -s in-progress

# 3. Implement
# ...

# 4. Check off acceptance criteria
beans update myproj-a3x1 \
  --body-replace-old "- [ ] Write test" \
  --body-replace-new "- [x] Write test"

# 5. Append Proof of Work (commands + results + residual)
beans update myproj-a3x1 --body-append "## Proof of Work

\
make vet   → 0\n\
make test  → PASS\n\
make lint  → 0 issues

Residual: none."

# 6. Close (only after PoW is present and verify passed)
beans update myproj-a3x1 -s completed
```

## Create an epic with tasks (draft-first)

This is the canonical tree shape: epic → tasks, two levels. The CLI
rejects a task under a task, so 10-minute work goes into a task's body
as acceptance-criteria checkboxes, not into child beans. The whole tree
starts in `draft` and is triaged in waves — epic first (research the
goal), then each task (research the requirement, write ACs).

```bash
# Epic (GOAL) — starts in draft
beans create "Auth system overhaul" -t epic -p high -s draft --tag epic
# → myproj-auth1

# After triaging the epic, promote and create the task children
beans update myproj-auth1 -s todo
beans create "Add OAuth provider"     -t task -s draft --parent myproj-auth1
beans create "Add 2FA support"        -t task -s draft --parent myproj-auth1
beans create "Wire auth into API"     -t task -s draft --parent myproj-auth1
```

**Rule:** each task is scoped so an entry-level subagent can complete it
without asking questions. If one grows past ~3 acceptance criteria,
split it into sibling tasks under the same epic.

## Found a bug: document, then triage

Stop. Do not write a fix yet.

```bash
beans create "CRS pending OR completed matches 0" -t bug -s draft --tag found-in-test
# → myproj-xxxx

beans show myproj-xxxx --body-only
```

Put in the draft body (via `--body-append` / `--body-replace-*`):

- Expected vs actual
- Stack, org, ids, times
- Evidence paths (`raw/NN-….log`, worker log)
- Open questions

Then triage (research the serving contract and the client) — delegate
to the best available research subagent with the strongest currently
reachable model (see **Who triages (binding)** in the parent
`SKILL.md`). Only then:

```bash
beans update myproj-xxxx -s todo
beans update myproj-xxxx -s in-progress
```

## Process-violation beans: root cause is the skipped step, not the symptom

When a shipped deliverable violates standing rules (style skills never
passed to the worker, comment rules breached), the cleanup bean records
BOTH layers:

- **Finding** — what shipped wrong, exact files.
- **Root cause** — which lifecycle step was skipped (usually: no
  `## Skills for coder` at triage, so the worker contract carried no rule
  paths and gates could not catch style).

Then close the loop on the artifact itself: triage read-only with the rules
skill LOADED so triage produces per-line verdicts (delete vs keep, and a
grep of sibling files to check whether the pattern is repo-wide local
style — local style wins over the abstract rule), promote, and dispatch
the coder with the skill path named as BINDING plus the verdict list.

The cleanup bean's PoW must include the rule-level check (e.g. a narration
grep returning 0), not just build/test gate colors — a style-cleanup bean
that only proves "tests pass" has not demonstrated its own AC.

## Find blocked work

```bash
beans list --json --is-blocked
```

## Group work into releases (tags, not `milestone` beans)

The CLI ships a `milestone` type; house rule: never create one. Tag-based
grouping does the same job:

```bash
beans update myproj-a3x1 --tag rel-v1
beans update myproj-b7k2 --tag rel-v1

# List everything in the release
beans list --json -S "rel-v1"
```
