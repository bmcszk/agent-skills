# CLI Reference

Full reference for every `beans` subcommand. For activation-relevant
workflows (tree shape, lifecycle, closure gates), see the parent
`SKILL.md`. This file is the flag-level lookup; the canonical example
of the **epic → task → subtask** tree with draft-first status is
[`patterns.md`](patterns.md).

All commands support `--json` for machine-readable output — agents
should always use it.

## Create

```bash
# Simple bug — starts in draft, needs triage before it can be claimed
beans create "Fix login redirect bug" -t bug -s draft -p high

# After triage (research, scope, acceptance criteria):
beans update myproj-a3x1 -s todo

# Feature with body from file
beans create "Implement OAuth flow" \
  -t feature -s draft -p normal \
  --body-file spec.md \
  --tag auth --tag security

# Task with parent and blocker
beans create "Add PKCE support" \
  -t task \
  --parent myproj-abc1 \
  --blocked-by myproj-xyz9 \
  --body "$(printf '## Acceptance Criteria\n\n- [ ] Generate code verifier\n- [ ] Store in session')"

# JSON output (always prefer for scripting/agents). New beans start as draft.
beans create --json "Deploy to staging" -t task -s draft
```

## List

```bash
# Tree view grouped by status
beans list

# All beans as JSON (agents always use --json)
beans list --json

# Beans ready to start (not blocked, active statuses)
beans list --json --ready

# Filter by type and status (multiple = OR logic)
beans list --json -t bug -t feature -s todo -s in-progress

# Exclude statuses
beans list --json --no-status completed --no-status scrapped

# Full-text search (Bleve syntax)
beans list --json -S "authentication"
beans list --json -S "login~"              # fuzzy
beans list --json -S "title:OAuth"         # field-scoped
beans list --json -S "auth AND session"    # AND logic

# Filter by relationship
beans list --json --is-blocked
beans list --json --parent myproj-abc1
beans list --json --no-parent              # top-level only

# Sort: created, updated, status, priority, id
beans list --json --sort priority

# Include full body in output
beans list --json --full

# Quiet mode: just IDs, one per line
beans list -q
```

## Show

```bash
# Human-readable
beans show myproj-a3x1

# JSON with full data including body and etag
beans show --json myproj-a3x1

# Multiple at once
beans show --json myproj-a3x1 myproj-b7k2

# Raw Markdown (frontmatter + body, for editing)
beans show --raw myproj-a3x1

# Body only (for piping)
beans show --body-only myproj-a3x1

# ETag only (for optimistic concurrency)
ETAG=$(beans show --etag-only myproj-a3x1)
```

## Update

```bash
# Change status
beans update myproj-a3x1 -s in-progress

# Multiple fields at once
beans update myproj-a3x1 \
  -s completed \
  -p normal \
  --title "Fix login redirect (resolved)"

# Replace exact text in body (must match exactly once)
beans update myproj-a3x1 \
  --body-replace-old "- [ ] Write test" \
  --body-replace-new "- [x] Write test"

# Append content to body
beans update myproj-a3x1 \
  --body-append "## Summary\n\nFixed redirect logic in auth middleware."

# Replace full body from file
beans update myproj-a3x1 --body-file updated-spec.md

# Relationship management
beans update myproj-a3x1 --parent myproj-epic1
beans update myproj-a3x1 --remove-parent
beans update myproj-a3x1 --blocking myproj-b7k2
beans update myproj-a3x1 --remove-blocking myproj-b7k2
beans update myproj-a3x1 --blocked-by myproj-c9m3

# Tag management
beans update myproj-a3x1 --tag backend --tag security
beans update myproj-a3x1 --remove-tag backend

# Optimistic concurrency (safe concurrent updates)
ETAG=$(beans show --etag-only myproj-a3x1)
beans update myproj-a3x1 --if-match "$ETAG" -s completed

# JSON output
beans update --json myproj-a3x1 -s in-progress
```
