---
name: beans
description: 'Beans task management CLI: create, list, update, close tasks/bugs/features alongside your code. Flat-file issue tracker for humans and agents. Every new bean starts as `draft` and must pass deep-research triage before promotion to `todo`. If you find a bug, document it as a draft, triage first, do not patch first. Tree structure: epic (one goal per session) -> task (one requirement) -> subtask (~10-min delegatable work). Use when you need to track work items, create tasks, manage bugs, organize epics, or query project state from the CLI.'
metadata:
  risk: none
  source: community
  date_added: '2026-05-12'
---
# Beans - Task Management

> CLI-based, flat-file issue tracker. Tasks live in `.beans/` as Markdown files, version-controlled alongside your code.

**Repo:** <https://github.com/hmans/beans>

Install, `beans init`, and agent-integration steps live in
[`references/setup.md`](references/setup.md).

## When to Use This Skill

- Managing project tasks, bugs, features from the CLI
- Letting coding agents track their work
- Creating, listing, updating, and closing beans
- Organizing work with milestones, epics, features, tags, priorities
- Querying project state with `beans list` filters

---

## Workflow Model

The lifecycle has levels (milestone → epic → feature → task/bug,
milestone optional) and a strict status progression. Read this
section before creating beans.

### Tree structure

Every bean lives in the type tree below. Bean `type` values are
`milestone` / `epic` / `feature` / `task` / `bug`.

| Level | What it represents | Bean `type` | Children |
|---|---|---|---|
| **Milestone** (optional) | A shippable checkpoint ("v1 works as a user"). Root only. | `milestone` | N epics |
| **Epic** | One GOAL - business/end-user outcome the project loops on until reached. | `epic` (program root: parentless `epic`, optionally under a milestone) | N features/tasks |
| **Feature** | One use case - a definable business/end-user requirement. | `feature` | N tasks |
| **Task** | One technical unit a worker agent delivers to complete a feature. | `task` or `bug` | none - leaf |
| **Subtask** | One ~10-minute piece of well-scoped, delegatable work. Hand it to a small subagent. | AC checkboxes inside the owning task (NOT a bean - the CLI rejects a task under a task) | none |

The hierarchy is enforced by the `parent` field - and by the CLI, which
REJECTS illegal parent/type combos at create time with an explicit error.
Enforcement matrix from beans v0.4.2 source (`ValidParentTypes` in
`internal/beancore/links.go`; probe with one throwaway create per level
before any bulk import; the CLI error is ground truth over any documented
convention): `milestone` parent ∈ {} (root only, nil); `epic` parent ∈
{milestone}; `feature` parent ∈ {milestone, epic}; `task`/`bug` parent ∈
{milestone, epic, feature}; a `task`/`bug` can NEVER be a parent. One
program = ONE parentless epic (the GOAL); its `## DECIDED` section
records program-level re-scope rules, never a milestone or side file.
Milestones are optional and only make sense for a versioned product
("v1"), not a single-goal project. A "support" epic is legal as a second epic under the same milestone:
technical non-business work such as lints, tests, tooling, git or CI
problems. It is not the session GOAL; keep one-goal-per-session
(below) for session focus. If a flat task later
genuinely needs bean children, convert it in place - `beans update <id>
-t epic` flips the type and preserves id/history (verified against the
CLI), making child creation legal. Probe any
hierarchy claim before relying on it. A documented convention the CLI
rejects poisons every recipe built on it. Where the CLI forbids an
extra level, keep 10-minute granularity as countable acceptance-criteria
checkboxes in the owning task instead of a separate bean.

Bulk-import recipe (ids are CLI-generated, so never assume them): create
ALL beans in pass 1 recording returned ids to a map; wire `--parent` /
`--blocked-by` in pass 2 from the map. If any type/parent error rejects
part of a batch, re-run as an idempotent repair script that reads the id
map and skips already-created beans.

```
milestone (optional, root - "v1")
├─ epic (THE GOAL)
│  ├─ feature (end-user use case)
│  │  ├─ task (worker-delivered unit)
│  │  └─ bug
│  └─ task
└─ epic "support" (lints, tests, tools - sibling, not the GOAL)
```

Subtasks are NOT beans (the CLI rejects a task under a task) - split a
task by adding acceptance-criteria checkboxes to its body, or create a
`feature` grouping when a requirement genuinely needs child beans.

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

- **`draft`** - needs triage. Research it before promoting. The body
  holds the question, links, unknowns, and the result of triage research.
- **`todo`** - actionable. Triage answered: scope is clear, acceptance
  criteria are written, references exist. Ready to claim.
- **`in-progress`** - claimed. Exactly one agent or human at a time.
- **`completed`** - verified. Body has `## Summary of Changes` + `##
  Proof of Work`.
- **`scrapped`** - killed. Body has `## Reasons for Scrapping`.

`beans list --ready` returns `todo` and `in-progress` beans. If you
find yourself about to claim a `draft`, you skipped triage - go back.

### Triage = deep research

A `draft` bean is a hypothesis. Before flipping to `todo`, the agent
or human triaging it must:

1. **Re-read the original request** - what is actually being asked?
2. **Deep research** - read the affected code, relevant docs, spec,
   prior art. Use online research (web search, Context7, vendor docs)
   when in-repo evidence isn't enough. Cite sources in the body.
3. **Scope the work** - split into tasks / subtasks. A requirement
   that is one fat bean is a smell; it should be an epic + children.
4. **Write acceptance criteria** - `- [ ]` checkboxes an outside
   reviewer can independently verify.
5. **Discover skills for the coding agent** - when the leaf will be
   implemented by a coder, scan the project's and the user's skill roots
   (`.agents/skills/`, `~/.agents/skills/`, and any agent-specific
   skill directory the runtime uses)
   and match by skill **description** to this stack and task. Write
   them into the bean body as:

   ```markdown
   ## Skills for coder

   - `~/.agents/skills/<name>/SKILL.md` - why this leaf needs it
   ```

   Do not hardcode a language or project pack. Re-discover per leaf.
   Coding subtasks without this section are not ready for `todo`.
   Passing a skill means naming its PATH in the dispatch and instructing
   the worker to read it fully before editing. Summarizing the skill's
   rules into the task context is NOT passing it: the summary drops
   whatever the summarizer did not think to include, and that gap is
   how a purged rule class re-ships under green gates. Skill rules a
   gate must verify get copied into the contract as explicit checkable
   items - build/lint/gofmt stay green while style rules are violated,
   so an unchecked style rule ships broken.
6. **Identify blockers and dependencies** - `--blocked-by` on children
   that can't start yet.
7. **Promote** - `beans update <id> -s todo` only when the body is
   research-backed, acceptance criteria exist, skills for coder are
   listed when coding will happen, and the bean is small enough to claim.

A `draft` that surfaces unanswerable questions is scrapped with the
questions written into `## Reasons for Scrapping`.

#### Who triages (binding)

Triage is done by the **best available research subagent**, not by
whoever happens to be around and not by the main session skimming the
ticket:

- **Pick the strongest available model dynamically at triage time** - query the agent runtime's own model-selection mechanism (its model
  list, router, or provider catalog) for the best currently-reachable
  reasoning model, and delegate to it. Do not hardcode a model name:
  the best choice changes over time and what is reachable varies per
  setup.
- The triage subagent works **read-only on the repo** (research, not
  implementation) and writes its findings into the bean body.
- Triage output contract - the draft body must end up with:
  1. **Root cause / answer to the open question** - with file:line
     references or cited URLs; "unknown" is not a triage result.
  2. **Local research** - affected code paths, configs, contracts read
     and summarized with paths.
  3. **Online research** - upstream docs/issues/specs consulted when
     in-repo evidence is insufficient; links recorded.
  4. **Scope** - tasks/subtasks split, ~10-min granularity at the
     bottom, with blockers wired via `--blocked-by`.
  5. **Acceptance criteria** - `- [ ]` checkboxes, independently
     verifiable.
  6. **Skills for coder** - when the leaf is for a coding agent:
     `## Skills for coder` with discovered skill paths (see triage
     step 5). Skip only for pure docs/ops leaves with no code edits.

Only when these are in the body may the triager run
`beans update <id> -s todo`. A `todo` bean whose body lacks root cause
or acceptance criteria is a triage failure - send it back to `draft`.
A coding leaf without `## Skills for coder` is also a triage failure.

### Found a bug (binding)

**If you find a bug, it needs to go through the correct beans process. It has to be documented, triaged first.**

Do not patch first. Do not jump to `todo` or `in-progress`. Do not "just fix it" because the test caught it.

1. **Stop coding.** Keep the evidence (httpyac logs, worker logs, failing test output).
2. **Document** - `beans create "<short title>" -t bug -s draft`. Body: what failed, expected vs actual, ids, times, stack, evidence paths.
3. **Triage** - deep research (code, contract, docs). Write acceptance criteria. Split if needed. Then `beans update <id> -s todo`.
4. **Claim** - only after triage: `beans update <id> -s in-progress`. Then implement.

A live mismatch is still a `draft` until triage says it is a real, scoped, actionable bug. Wrong env, empty data, or an unsupported type is not a silent code change.

Recipe: [`references/patterns.md`](references/patterns.md#found-a-bug-document-then-triage).
Reopen flow: [`references/reopen-pattern.md`](references/reopen-pattern.md).
Code-fix bean creation: [`references/all-code-delegated.md`](references/all-code-delegated.md).

## CLI Commands

Every subcommand and flag is documented in
[`references/cli.md`](references/cli.md). This section is a quick
top-of-mind index for the four commands an agent uses in 95% of
sessions.

| Command | When to reach for it |
|---|---|
| `beans prime` | Session start - load the project's current bean state. |
| `beans list --json` | Browse / filter. `--ready` for post-triage work, `-s draft` for triage queue, `--no-parent` for top-level (epics). |
| `beans create` | New bean. Default `-s draft`; promote with `update -s todo` after triage. |
| `beans update` | Claim, progress, append PoW, close. Use `--body-replace-old/new` for targeted edits, `--body-append` for `## Summary of Changes` and `## Proof of Work`. |
| `beans show` | Inspect. `--body-only` for piping, `--etag-only` for safe concurrent updates. |

For the on-disk file format (YAML frontmatter, filename convention,
field schema) see [`references/bean-file-format.md`](references/bean-file-format.md).
The CLI owns that file - never hand-edit `.beans/*.md`.

### Write-back comments (audit verdicts, review notes)

There is NO `beans comment` subcommand. Attach dated notes to a bean with
the CLI; patterns and wording: read
[`references/write-back-comments.md`](references/write-back-comments.md)
when writing audit verdicts or review notes back to a bean.

### Prime Context

```bash
beans prime
```

Outputs context about the project's current beans, priorities, and recommended next actions. Agents should run this at session start.

### Delegation patterns

When dispatching bean work to subagents (especially small or free models):

- **Short prompts.** One goal, exact commands, file paths. Inline design loses fidelity.
- **Design decisions go in the bean body.** Keep the full design inside the task via `--body-replace-old/new`; the bean is the single source of truth. Do not scatter design across scratch files.
- **One stall = change tactic.** Hangs and text-only returns are signals - do not retry with the same prompt. Switch task size, agent, or toolset. Two failures = stop delegating that step.
- **Bypass wrappers for diagnostics.** Use raw commands when reading exact errors or lint positions.

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

The orchestrator, not the worker, owns steps 7-10: a worker report is a
claim. Re-run the gates, read the diff, write the PoW in the bean body -
a completion recorded only in chat is not in the tracker. For every-file
tasks the PoW states the live file count, the verdict count, and the
command proving the sets match. Count parity plus green gates prove
coverage, not substance: re-read the diff of every fixed file and
spot-read clean ones before closing a sweep. A worker can stamp verdicts
while breaking style rules no gate checks; a close on verdict counts
alone gets reopened.

A repo may add its own beans lint that checks more than the CLI; if it
has one, run it after every bean change. Check that a skill path exists
on disk before writing it into a bean body.

A mis-typed bean (a `task` that needs children) converts IN PLACE with
`beans update <id> -t epic`; id, body, and history survive. Scrap and
recreate orphans the audit trail - reserve scrapping for genuinely dead
goals.

When a triage verdict arrives AFTER a fix pass already shipped, append
it to the same bean body and run the delta as a follow-up pass under
that bean. Do not open a second bean for the same scope, and do not
drop the stricter verdicts because a first pass already went green.

For epics, steps 8–9 are replaced by: end-to-end tests covering the full epic +
a `## Proof of Work` section that exercises the goal as a user would.
See **Closure gates (binding)** below.

### Triage-to-claim (binding)

- A `draft` is **not** in `beans list --ready`. You cannot claim it.
- To work on it: triage first (research, scope, acceptance criteria,
  `--blocked-by` on children), then `beans update <id> -s todo`. Only
  then does it become claimable.
- Skipping triage to flip a bean straight to `todo` is a process
  violation - same category as marking `completed` without testing.

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

- The exact commands run (build, test, lint, smoke check - whatever
  applies).
- The observed result for each command (exit status, key signal: counts,
  pass/fail, output fingerprint).
- A `Residual:` line - named leftovers, or `none`.

If `## Proof of Work` is missing, the closure is rejected. Append it
first, then mark completed:

```bash
beans update myproj-a3x1 --body-append "## Proof of Work
<build>    → exit 0
<test>     → PASS (148s)
<lint>     → 0 issues

Residual: none."
beans update myproj-a3x1 -s completed
```
Placeholders stand for the project's own build/test/lint entry points;
an example never presumes a stack. The verify gate is itself binding:
run the project's tests/build/lint and observe the result. Red gate =
fix the root cause; cannot verify = leave `in-progress` and say so.

#### 2. Epic closure

**An epic cannot be closed while any of its tasks or subtasks are still
open, and cannot be closed without full end-to-end tests + `## Proof of
Work`.** Two-part gate:

- **No open children.** Every task and subtask under the epic must be
  `completed` or `scrapped` before the epic itself can move to
  `completed`. Check with:

  ```bash
  # Find any non-terminal child of the epic
  beans list --json --parent myproj-epic --no-status completed --no-status scrapped
  # Empty output → safe to close the epic.
  ```

- **Full end-to-end tests + `## Proof of Work`.** The epic's proof is
  *integration-level*: not just "the unit tests passed", but evidence
  the goal as a whole was reached end-to-end. Append a `## Proof of
  Work` section whose commands cover:

  - The full test suite (unit + integration + e2e, where they exist).
  - Any end-to-end / smoke checks that exercise the goal as a user
    would (browser, CLI invocation, API roundtrip, etc.).
  - For build/deploy epics, the live artifact and its reachable URL or
    version.

A goal that says "ships feature X" without exercising X end-to-end is
not proven. No e2e harness exists? Say so under `Residual:` with the
reason - silent omission is a violation.

These proof rules apply to **every** bean type: no Proof of Work, no
`completed`.

### Commit Message Convention

Include bean IDs in commit messages:

```
feat(auth): add OAuth PKCE support

Refs: myproj-a3x1
```

---

## Anti-Patterns

Process and CLI hygiene - not the closure rules, which live in
**Closure gates (binding)** above.

| Don't | Do |
|-------|-----|
| Skip `beans prime` at session start | Run it first, every session |
| Scripts without `--json` | `--json` for machine-readable output |
| Edit `.beans/` files directly | Use CLI commands |
| Ignore etag for concurrent updates | Use `--if-match` for safe concurrent edits |
| Use `--body-file` for small changes | Use `--body-replace-old/new` for targeted edits |
| Forget to update status when starting work | Set `-s in-progress` when claiming a task |
| Leave beans in `in-progress` when done | Always close with `-s completed` or `-s scrapped` |
| Two active epics in one session | One GOAL per session, loop until reached |
| Bug found, patch immediately | `beans create -t bug -s draft`, document, triage, claim |
| Close work and leave state artifacts behind | Before ending a session: PR title/body match HEAD, every touched bean terminal (`completed`/`scrapped`), epic titles non-empty, no orphan drafts |
| Set bean statuses without the CLI or leave `todo` epics that already shipped | Session-end sweep: `beans list`, close or scrap every bean the shipped work covers; an epic's status mirrors the work, not the plan |
| Append `--body-append` PoW before checking the worker's claims | Parent re-runs gates + reads the diff FIRST; PoW records YOUR gate output, not the worker's report |
| Hand-edit `.beans/*.md` to attach a comment | `beans update --body-append "## LABEL (context): ..."` - no comment subcommand exists; the CLI owns the file |
| Create with only `-d` and fix the title later | Pass the title positionally at create - the filename slug is permanent, later `--title` edits don't rename it |

---

## References

- **Repo:** https://github.com/hmans/beans
- **Releases:** https://github.com/hmans/beans/releases
- **Docs (Context7):** https://context7.com/hmans/beans/llms.txt
