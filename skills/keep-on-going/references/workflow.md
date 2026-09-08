# Workflow — One Epic Session

A linear recipe for the loop described in the parent `SKILL.md`. Use
this when you've just claimed an epic and need to drive it forward
without losing the discipline.

## 1. Open the session

```bash
beans prime
beans list --json --no-parent -s draft -s todo -s in-progress
```

You should see one active epic. If you see more than one, close the
extras or stop and ask the user which one to focus on.

```bash
beans show --json <epic-id>
```

Read the epic body. It has:

- **Acceptance criteria** as `- [ ]` boxes.
- A goal statement at the top.
- Possibly children already in `draft` (research done) or `todo`
  (triaged).

## 2. Walk the tree top-down for triage

Triage moves beans from `draft` to `todo`. Always triage the parent
before its children — a task whose epic isn't ready is wasted work.

```text
epic (draft) → research the goal, set acceptance criteria → todo
  task       → research the requirement, scope, blockers → todo
    subtask  → research the 10-min piece, write the body → todo
```

For each bean you triage, append to its body:

- The acceptance criteria (≤3 per subtask; ≤5 per task; epic-level
  criteria are whatever the goal needs).
- The `--blocked-by` children that depend on earlier work.
- A `## Triage notes` section with cited research.

After triage, the bean becomes claimable via `beans list --ready`.

## 3. Claim and work the next ready bean

```bash
beans list --json --ready
beans update <id> -s in-progress
```

Now run the four-pass leaf work (see [`leaf.md`](leaf.md)). Update the
body as you go:

```bash
# Check off an acceptance criterion
beans update <id> \
  --body-replace-old "- [ ] Write test" \
  --body-replace-new "- [x] Write test"
```

## 4. Prove before close

Run the verification commands. Observe the result. Append the proof
**before** the close:

```bash
beans update <id> --body-append "## Proof of Work

\
make vet   → 0\n\
make test  → PASS (unit + integration + e2e, 148s)\n\
make lint  → 0 issues

Residual: none."

beans update <id> -s completed
```

If the verify gate is red: fix the root cause. If you can't verify,
leave the bean `in-progress` and say so. There is no "I think it
works" close.

## 5. Audit and loop

After closing a leaf, look up:

```bash
beans list --json --parent <epic-id> --no-status completed --no-status scrapped
```

Two outcomes:

- **Empty** — every child is done. Move to step 6.
- **Non-empty** — there are still children. Pick the next ready one,
  go to step 3. Or: if the remaining work exceeds what the epic can
  absorb, scrap or split the epic.

## 6. Close the epic

Two-part gate, both binding:

```bash
# Part 1: no open children
beans list --json --parent <epic-id> \
  --no-status completed --no-status scrapped
# (must be empty)

# Part 2: comprehensive tests + Proof of Work for the goal
beans update <epic-id> --body-append "## Proof of Work

\
# Full test suite (unit + integration + e2e)
make test  → PASS
# End-to-end smoke checks (one per surface of the goal)
curl -fsS https://staging.example.com/healthz  → 200 OK in 84ms
# Live artifact, if applicable
kubectl rollout status deployment/api --timeout=120s  → 'successfully rolled out'

Residual: none."

beans update <epic-id> -s completed
```

Comprehensive tests ≠ "the unit tests passed". The proof has to
exercise the goal as a user would. If a goal is "feature X works",
the proof must show X working end-to-end. If a goal is "deploy to
prod", the proof must show the live artifact reachable from outside.

If a gate cannot be run (no e2e harness exists for this project),
write it explicitly into `Residual:` with the reason. Silent omission
is a violation.

## 7. Park the session

The session is done when one of:

- The epic is `completed`.
- The epic is `scrapped` with a reason.
- The session has run out of useful work and the user has been asked.

A session that ends with the epic still `in-progress` and no
children to work on is a stuck session. Diagnose; don't pretend.