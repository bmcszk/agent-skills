---
name: beans
description: 'Beans task management CLI: create, list, update, close tasks/bugs/features alongside your code. Flat-file issue tracker for humans and agents. Every new bean starts as `draft` and must pass deep-research triage before promotion to `todo`. If you find a bug, document it as a draft, triage first, do not patch first. Tree structure: epic (one goal per session) -> task (one requirement) -> subtask (~10-min delegatable work). Use when you need to track work items, create tasks, manage bugs, organize epics/milestones, or query project state from the CLI. Keywords: beans, task management, issue tracker, create task, close task, list tasks, bug tracking, project management, draft triage, epic task subtask, found a bug.'
metadata:
  risk: none
  source: community
  date_added: '2026-05-12'
---
# Beans — Task Management

> CLI-based, flat-file issue tracker. Tasks live in `.beans/` as Markdown files, version-controlled alongside your code.

**Repo:** <https://github.com/hmans/beans> (760+ stars)

Install, `beans init`, and agent-integration steps live in
[`references/setup.md`](references/setup.md).

## When to Use This Skill

- Managing project tasks, bugs, features from the CLI
- Letting coding agents track their work
- Creating, listing, updating, and closing beans
- Organizing work with epics, milestones, tags, priorities
- Querying project state with `beans list` filters

---

## Workflow Model

The lifecycle has three levels and a strict status progression. Read this
section before creating beans.

### Tree structure

Every bean lives in a three-level tree. Names below are conventions, not
bean `type` values — the `type` is still `task` / `bug` / `feature` /
`idea`.

| Level | What it represents | Bean `type` | Children |
|---|---|---|---|
| **Epic** | One GOAL. The outcome a session loops on until reached. | `feature` (or `bug` for a single-issue goal) | N tasks |
| **Task** | One requirement, issue, or capability needed to reach the goal. | `task` or `bug` | N subtasks |
| **Subtask** | One ~10-minute piece of well-scoped, delegatable work. Hand it to a small subagent. | `task` | none |

The hierarchy is enforced by the `parent` field. A bean has **at most
one** parent; epics have no parent (`beans list --no-parent`).

```
epic (GOAL)
├─ task (requirement)
│  ├─ subtask (10-min piece of work)
│  └─ subtask
└─ task
```

### One goal per session

An epic IS the session's goal. Pick **at most one** active epic and loop
on it until the goal is reached or scrapped. Two open epics = split
focus = slower. `beans list --ready` is the natural heartbeat; treat
the epic as done when its acceptance criteria are checked and the last
child is `completed`.

### Status progression: every bean starts as `draft`

**Default initial status: `draft`.** No bean is created directly as
`todo`. A bean must pass triage (deep research) before it is
actionable.

```
draft  →  todo  →  in-progress  →  completed
                 ↘  scrapped
```

- **`draft`** — needs triage. Research it before promoting. The body
  holds the question, links, unknowns, and the result of triage research.
- **`todo`** — actionable. Triage answered: scope is clear, acceptance
  criteria are written, references exist. Ready to claim.
- **`in-progress`** — claimed. Exactly one agent or human at a time.
- **`completed`** — verified. Body has `## Summary of Changes` + `##
  Proof of Work`.
- **`scrapped`** — killed. Body has `## Reasons for Scrapping`.

`beans list --ready` returns `todo` and `in-progress` beans. If you
find yourself about to claim a `draft`, you skipped triage — go back.

### Triage = deep research

A `draft` bean is a hypothesis. Before flipping to `todo`, the agent
or human triaging it must:

1. **Re-read the original request** — what is actually being asked?
2. **Deep research** — read the affected code, relevant docs, spec,
   prior art. Use online research (web search, Context7, vendor docs)
   when in-repo evidence isn't enough. Cite sources in the body.
3. **Scope the work** — split into tasks / subtasks. A requirement
   that is one fat bean is a smell; it should be an epic + children.
4. **Write acceptance criteria** — `- [ ]` checkboxes an outside
   reviewer can independently verify.
5. **Identify blockers and dependencies** — `--blocked-by` on children
   that can't start yet.
6. **Promote** — `beans update <id> -s todo` only when the body is
   research-backed, acceptance criteria exist, and the bean is small
   enough to claim.

A `draft` that surfaces unanswerable questions is scrapped with the
questions written into `## Reasons for Scrapping`.

### Found a bug (binding)

**If you find a bug, it needs to go through the correct beans process. It has to be documented, triaged first.**

Do not patch first. Do not jump to `todo` or `in-progress`. Do not "just fix it" because the test caught it.

1. **Stop coding.** Keep the evidence (httpyac logs, worker logs, failing test output).
2. **Document** — `beans create "<short title>" -t bug -s draft`. Body: what failed, expected vs actual, ids, times, stack, evidence paths.
3. **Triage** — deep research (code, contract, docs). Write acceptance criteria. Split if needed. Then `beans update <id> -s todo`.
4. **Claim** — only after triage: `beans update <id> -s in-progress`. Then implement.

A live mismatch is still a `draft` until triage says it is a real, scoped, actionable bug. Wrong env, empty data, or an unsupported type is not a silent code change.

Recipe: [`references/patterns.md`](references/patterns.md#found-a-bug-document-then-triage).

---

## CLI Commands

Every subcommand and flag is documented in
[`references/cli.md`](references/cli.md). This section is a quick
top-of-mind index for the four commands an agent uses in 95% of
sessions.

| Command | When to reach for it |
|---|---|
| `beans prime` | Session start — load the project's current bean state. |
| `beans list --json` | Browse / filter. `--ready` for post-triage work, `-s draft` for triage queue, `--no-parent` for top-level (epics). |
| `beans create` | New bean. Default `-s draft`; promote with `update -s todo` after triage. |
| `beans update` | Claim, progress, append PoW, close. Use `--body-replace-old/new` for targeted edits, `--body-append` for `## Summary of Changes` and `## Proof of Work`. |
| `beans show` | Inspect. `--body-only` for piping, `--etag-only` for safe concurrent updates. |

For the on-disk file format (YAML frontmatter, filename convention,
field schema) see [`references/bean-file-format.md`](references/bean-file-format.md).
The CLI owns that file — never hand-edit `.beans/*.md`.

---

## Bean File Format

Beans are Markdown files in `.beans/` with YAML frontmatter. The CLI
owns the format; full schema and example in
[`references/bean-file-format.md`](references/bean-file-format.md).

---

## Workflow Patterns

The recipes live in [`references/patterns.md`](references/patterns.md):
**Start work on a bean** (claim → implement → check off → PoW → close)
and **Create an epic with tasks and subtasks** (the canonical draft-first
tree shape). Find-blocked and milestones are one-liners in that file.

---

## Agent Workflow

### Prime Context

```bash
beans prime
```

Outputs context about the project's current beans, priorities, and recommended next actions. Agents should run this at session start.

### Agent Task Lifecycle

```
1. beans prime                          → Get project context
2. beans list --json -s draft           → Find beans awaiting triage
3. Research the draft, scope it, write  → Triage the bean
   acceptance criteria, then promote
   with `beans update <id> -s todo`
4. beans list --json --ready            → Find actionable work
5. beans update <id> -s in-progress     → Claim the task
6. ... implement the change ...
7. beans update <id> --body-replace-*   → Check off acceptance criteria
8. VERIFY: run the project's tests/build/lint and observe results   ← gate
9. beans update <id> --body-append      → Add ## Proof of Work (commands + results + residual)
10. beans update <id> -s completed      → Mark done (only after verify + proof are present)
```

For epics, steps 8–9 are replaced by: comprehensive end-to-end tests +
a `## Proof of Work` section that exercises the goal as a user would.
See **Closure gates (binding)** below.

### Triage-to-claim (binding)

- A `draft` is **not** in `beans list --ready`. You cannot claim it.
- To work on it: triage first (research, scope, acceptance criteria,
  `--blocked-by` on children), then `beans update <id> -s todo`. Only
  then does it become claimable.
- Skipping triage to flip a bean straight to `todo` is a process
  violation — same category as marking `completed` without testing.

### Closure gates (binding)

Two rules. Both apply to every `beans update -s completed` call. A bean
that fails either rule stays in `in-progress` (or `draft`/`todo` if
triage never finished); `scrapped` is the only honest exit when the
work cannot be completed.

#### 1. Task / subtask closure

**A task or subtask cannot be closed without a `## Proof of Work` section
in its body.** The section is the evidence the verify gate ran, separate
from `## Summary of Changes` (which records what changed). It must
contain, at minimum:

- The exact commands run (build, test, lint, smoke check — whatever
  applies).
- The observed result for each command (exit status, key signal: counts,
  pass/fail, output fingerprint).
- A `Residual:` line — named leftovers, or `none`.

If `## Proof of Work` is missing, the closure is rejected. Append it
first, then mark completed:

```bash
beans update myproj-a3x1 --body-append "## Proof of Work

\
make vet   → 0\n\
make test  → PASS (unit + integration + e2e, 148s)\n\
make lint  → 0 issues (452 → 0)

Residual: none."

beans update myproj-a3x1 -s completed
```

The verify gate that produces the proof is itself binding. "I think it
works" is not completion. Run the project's tests/build/lint and
observe the result. If the gate is red, fix the root cause; if you
cannot verify, leave the bean `in-progress` and say so.

#### 2. Epic closure

**An epic cannot be closed while any of its tasks or subtasks are still
open, and cannot be closed without comprehensive tests + `## Proof of
Work`.** Two-part gate:

- **No open children.** Every task and subtask under the epic must be
  `completed` or `scrapped` before the epic itself can move to
  `completed`. Check with:

  ```bash
  # Find any non-terminal child of the epic
  beans list --json --parent myproj-epic --no-status completed --no-status scrapped
  # Empty output → safe to close the epic.
  ```

- **Comprehensive tests + `## Proof of Work`.** The epic's proof is
  *integration-level*: not just "the unit tests passed", but evidence
  the goal as a whole was reached end-to-end. Append a `## Proof of
  Work` section whose commands cover:

  - The full test suite (unit + integration + e2e, where they exist).
  - Any end-to-end / smoke checks that exercise the goal as a user
    would (browser, CLI invocation, API roundtrip, etc.).
  - For build/deploy epics, the live artifact and its reachable URL or
    version.

A goal that says "ships feature X" without exercising X end-to-end is
not proven. If a gate cannot be run (no e2e harness exists for this
project), write that explicitly into `## Proof of Work` under
`Residual:` with the reason — silent omission is a violation.

Closing an epic with open children, or without comprehensive tests +
Proof of Work, is a process violation — same category as closing a
task without `## Proof of Work`.

---

### No Proof of Work, no `completed`

Applies to **every** bean type. The two subsections above define *what
counts as proof* for tasks/subtasks vs epics; this is the underlying
rule that no bean escapes.

### Commit Message Convention

Include bean IDs in commit messages:

```
feat(auth): add OAuth PKCE support

Refs: myproj-a3x1
```

---

## Anti-Patterns

Process and CLI hygiene — not the closure rules, which live in
**Closure gates (binding)** above.

| Don't | Do |
|-------|-----|
| Skip `beans prime` at session start | Always run `beans prime` first |
| Use `beans list` without `--json` in scripts | Always use `--json` for machine-readable output |
| Edit `.beans/` files directly without CLI | Use CLI commands for consistency |
| Ignore etag for concurrent updates | Use `--if-match` for safe concurrent edits |
| Use `--body-file` for small changes | Use `--body-replace-old/new` for targeted edits |
| Forget to update status when starting work | Set `-s in-progress` when claiming a task |
| Leave beans in `in-progress` when done | Always close with `-s completed` or `-s scrapped` |
| Open two active epics in one session | Pick one GOAL per session, loop on it until reached |
| Find a bug and patch it immediately | `beans create -t bug -s draft`, document evidence, triage, then claim |

---

## References

- **Repo:** https://github.com/hmans/beans
- **Releases:** https://github.com/hmans/beans/releases
- **Docs (Context7):** https://context7.com/hmans/beans/llms.txt

---

> **Remember:** Always `beans prime` first. Use `--json` for scripts. Close your beans.

## When to Use
This skill is applicable when managing project tasks, bugs, or features using the Beans CLI issue tracker.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

### Delegation Patterns

When dispatching to subagents (especially free/small models):

- **Short prompts.** One goal, exact commands, file paths. Inline design loses fidelity.
- **Externalize plans.** Put >2 design decisions in `plan.md`, reference by path. Don't paste 4KB of design into the task.
- **One stall = change tactic.** Hangs and text-only returns are signals — do NOT retry with the same prompt. Switch task size, agent, or toolset. Two failures = stop delegating that step.
- **Bypass rtk for diagnostics.** Use raw commands when reading exact errors or lint positions.
