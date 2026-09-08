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

## Create an epic with tasks and subtasks (draft-first)

This is the canonical tree shape. The whole tree starts in `draft` and
is triaged in waves — epic first (research the goal), then each task
(research the requirement), then each subtask (scope the 10-min piece).

```bash
# Epic (GOAL) — starts in draft
beans create "Auth system overhaul" -t feature -p high -s draft --tag epic
# → myproj-auth1

# After triaging the epic, promote and create the task children
beans update myproj-auth1 -s todo
beans create "Add OAuth provider"     -t task -s draft --parent myproj-auth1
beans create "Add 2FA support"        -t task -s draft --parent myproj-auth1
beans create "Wire auth into API"     -t task -s draft --parent myproj-auth1

# Triage each task, then split into 10-min subtasks:
beans create "Add OAuth PKCE verifier"   -t task -s draft --parent myproj-oauth1
beans create "Add OAuth state param"     -t task -s draft --parent myproj-oauth1
beans create "Add OAuth token exchange"  -t task -s draft --parent myproj-oauth1
```

**Rule:** a subtask is one ~10-minute piece of work an entry-level
subagent can complete without asking questions. If the body needs more
than 3 acceptance criteria, it is probably a task, not a subtask.

## Find blocked work

```bash
beans list --json --is-blocked
```

## Organize into milestones

```bash
# Tag-based grouping
beans update myproj-a3x1 --tag milestone-v1
beans update myproj-b7k2 --tag milestone-v1

# List everything in a milestone
beans list --json -S "milestone-v1"
```
