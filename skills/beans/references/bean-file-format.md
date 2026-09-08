# Bean File Format

Beans are Markdown files in `.beans/` with YAML frontmatter. The CLI
owns this format — do not hand-edit the files; use `beans update`.

```markdown
---
title: Fix login redirect bug
status: in-progress
type: bug
priority: high
tags:
    - auth
    - security
created_at: 2025-01-10T08:00:00Z
updated_at: 2025-01-15T14:22:00Z
parent: myproj-epic-auth
blocking:
    - myproj-deploy1
blocked_by: []
---

## Problem

After OAuth login, users are redirected to `/` instead of the
originally requested URL.

## Acceptance Criteria

- [x] Capture redirect_uri in session
- [ ] Restore redirect after callback
- [ ] Write integration test
```

## Filename convention

`<prefix><id>--<slug>.md` — e.g., `myproj-a3x1--fix-login-redirect-bug.md`

## Metadata fields

| Field | Values | Description |
|---|---|---|
| `status` | `draft`, `todo`, `in-progress`, `completed`, `scrapped` | Bean lifecycle state |
| `type` | `task`, `bug`, `feature`, `idea`, custom | Category of work |
| `priority` | `low`, `normal`, `high`, `critical` | Urgency level |
| `tags` | Any string, multiple allowed | Freeform categorization |
| `parent` | Bean ID | Parent bean (for epics/subtasks) |
| `blocking` | List of bean IDs | Beans this one blocks |
| `blocked_by` | List of bean IDs | Beans blocking this one |

See [`cli.md`](cli.md) for the update commands that mutate these fields.
