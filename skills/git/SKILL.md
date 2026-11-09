---
name: git
description: >-
  Use when working with git in any repo under PR flow: starting work on a
  branch, updating a stale branch, resolving conflicts, rebasing, naming
  branches or commits, watching CI, cleaning up after a merged PR, or
  managing worktrees. Carries the house laws: squash-merge PRs, merge over
  rebase to avoid force pushes, humans merge, CI must stay green, worktrees
  only for parallel work inside .worktrees/. Not for GitHub API or gh CLI
  details (see github skill) or git internals.
license: MIT
metadata:
  audience: developers
  workflow: pr-flow
  category: dev
  technologies: git, github, ci
---

# Git

One integration branch (`master`). Work lands only through PRs,
squash-merged by a human with CI green. Everything else below is how to
stay out of git's way.

## Open only real PRs (verify the diff before create)
A squash commits whatever is ON the branch at merge time, not what the
PR description promised - so a branch carrying extra parked commits gets
them silently absorbed, and a follow-up PR on the same branch can open
diffing EMPTY against master. Before `gh pr create`, verify the branch
actually differs:

```bash
git fetch origin && git diff origin/master...HEAD --stat   # empty => phantom
```

Empty stat while `git log origin/master..HEAD` still lists commits =
the content is already on master via an earlier squash: do NOT create
the PR; if one is already open, close it as superseded (say where the
content landed), delete the branch, and tell the user immediately - a
phantom PR wastes the human gate. Prevention: one branch per PR, and
never park later-phase commits on a branch whose PR is awaiting merge.
Group features into ONE PR when they belong together (gate + port on
one feature = one PR; a RED gate alone is a separate PR only when the
port cannot exist without master-side fixtures). Check the PR right
after create: draft must be flipped (`gh pr ready <n>`) and the title
must be the real one (`gh pr edit <n> --title ...`) - `gh pr create`
can land a draft with a boilerplate title, and a draft with the wrong
title is not a deliverable.

## Start of work (new branch)

Checklist before a single line of work:

```bash
git checkout master
git pull origin master          # local master == origin/master
git fetch --prune --prune-tags  # prunes stale remote refs and tags
git worktree prune             # drop metadata of removed worktrees
git branch --merged master | grep -v master | xargs -r git branch -d
git switch -c <type>/<short-desc>   # from fresh master
```

The merged-branch sweep: `git branch -d` refuses unmerged branches, so it
is safe as written - and under squash-merge it catches nothing from
merged PRs (new SHAs); squash debris falls to the cleanup law below.
Verify nothing else claims the name: `git branch -a
--list <type>/*` and `git ls-remote --heads origin <type>/*`. Never
branch from another feature branch unless the work depends on it; if it
does, name the base branch in the PR description.

### One open PR per branch; few open PRs total

Stacked-PR waves rot. Every open PR ages against master while it waits,
and each later merge re-dirties every branch that touched the same files
(observed cost: two of three parallel PRs needed dedicated merge
sessions, one twice). Laws:

- Branch each lane from current master; never from another open lane's
  branch unless the work truly depends on it (then name the base in the
  PR body and expect a re-merge per upstream merge).
- Keep the number of simultaneously open PRs minimal - ideally one per
  repo, two only when they touch disjoint file sets. Disjoint means
  disjoint: shared README/manifest/fixture dirs are NOT disjoint.
- Sequence same-area work: open PR N+1 only after N merges (or after
  refreshing N+1's branch with a merge from master - see "Refreshing a
  branch").
- Between any two merges, refresh every other open branch that shares
  files with what just merged (`gh pr view <n> --json mergeable` shows
  CONFLICTING the moment it rots). Do not let the user discover the rot.

### Branch naming

`<type>/<short-kebab-desc>`: `feat/`, `fix/`, `hotfix/`, `chore/`,
`docs/`, `refactor/`, `test/`. Lowercase kebab-case, no bare issue
numbers alone, optional suffix `-<bean-id-suffix>` allowed.
Examples: `feat/oauth-login`, `fix/flaky-user-test`,
`chore/deps-weekly`, `docs/readme-install`.

### Commit naming

Conventional Commits, imperative present ("add", not "added"):
`type(scope): summary`, ≤72 chars, lowercase after colon, no trailing
period. Body wraps at 72, explains what/why not how. Types mirror branch
types. Examples: `feat(auth): add PKCE login flow`,
`fix(parser): clamp negative turn counts`.

## Keep the branch shippable

**PR health first, above any other work.** The moment a PR is open, its
greenness outranks new lanes, new features, and new PRs. Concretely:

- Poll every open PR's health before starting anything new:
  `gh pr view <n> --json mergeable,mergeStateStatus,statusCheckRollup`.
  CONFLICTING/DIRTY = drop what you are doing and fix it (merge from
  master, resolve, gates, push). A failing check = root-cause and fix.
- A red PR blocks everything else in the repo: never open, never review,
  never start a new lane while any open PR is red or dirty. Fix the red
  one first, then resume the queue.
- One red PR left unattended while a new PR is opened is a sequencing
  bug, not bad luck - the new PR's merge will re-dirty the red one
  (observed: a fold PR went dirty while attention moved to the other
  merges in the same wave).
- After fixing, re-verify health before reporting: `gh pr view <n>
  --json mergeable` must read CLEAN and the checks line must be all
  green (or carry only a disclosed intentional-RED with the PR body
  naming it).

**"Status?" means "convince me nothing is rotting."** When the user asks
for status, they are expressing concern that something is stuck, broken,
or unattended - not requesting a narration of the last log lines. A good
status reply therefore PROVES health with fresh evidence, gathered in the
same turn:

- Re-run the health probes live (`gh pr view` for every open PR, checks,
  branch tips vs remote, worktree/branch debris count, CI rollup) - never
  replay remembered state; stale "it was green 20 minutes ago" is the
  failure mode being probed for.
- Lead with any NON-green item and its unblock ETA. If a fix is in
  flight, say what is happening at the GIT level (merge in progress,
  gates running, push pending) and what YOU will do if it does not
  finish (fix it yourself, re-dispatch). An in-flight item without
  a named fallback reads as "nobody is watching it".
- End with the single next action and its trigger. No status reply may
  end on "waiting" alone - if the only blocker is a human merge, say
  exactly that; if the blocker is your own work, you own the watching.
- Gate or count evidence is SHA-scoped: quote numbers only from the tree
  you verified at the SHA you name. A stale or detached checkout
  fabricates health (phantom package counts, files master deleted still
  "present") - sync it first before quoting anything.
- When anything but this shell does the push (helper, hook, another
  session), it inherits nothing from this environment: an unset
  commit-signing agent socket stalls a finished merge at push time.
  Set the env line in the same invocation as the push, and know the
  no-force recovery rule: amend only never-pushed commits, else a
  fixup commit.

CI status is part of the work, not an afterthought:

- Watch from push: `gh pr checks <PR>` (or `gh run watch`). No "looks
  done" without the checks line: every job `pass`.
- Red = stop and fix the root cause; never merge red, never re-run to
  green a flake without understanding the flake.
- One fix = one new commit; do not amend pushed commits.
- If master moved, refresh before pushing again.

### Refreshing a branch: merge, do not rebase

Default refresh of a stale branch is a merge that can push normally:

```bash
git fetch origin
git merge origin/master        # or: git merge-base --is-ancestor \
                               # origin/master HEAD && echo up-to-date
git push                       # ordinary push, no force
```

A rebase rewrites your pushed commits, so the push needs `--force` /
`--force-with-lease`, which can destroy teammates' pushes. Prefer the
merge. If a rebase is truly required (user asks, or a rebase-merge
policy), wait for the working tree to be clean first (commit or stash),
rebase only unpushed commits when possible, and if history was already
pushed, push back with `--force-with-lease` (never bare `--force`), and
say what you overwrote.

### Enforce merge-over-rebase in config, not just in habit

`pull.rebase` / `branch.<name>.rebase` in any gitconfig silently
rewrites on every `git pull` - the exact force-push bait this section
bans. Audit config before trusting a repo to obey the law:

```bash
git config --show-origin --get-regexp '^(pull\.rebase|branch\.[^.]+\.rebase)'
```

The durable fix is global `pull.ff = only`: pulls merge by default, and
a diverged pull refuses loudly ("Not possible to fast-forward") instead
of rewriting. Local repo config beats the global, so sweep the clones
too:

```bash
git config --local --get-regexp '^(pull\.rebase|branch\.[^.]+\.rebase)'
```

Prove a pull-policy change behaviorally, not by key presence: bare
origin + two clones in a sandbox, push one commit from each, then
`git pull` in the first - it must FAIL with the fast-forward refusal.
A pull that succeeds means the test never diverged (the second clone's
commit was never pushed).

Machine setup and config audits: read
[references/setup.md](references/setup.md).

### Common base (where branches diverged)

Find it before any rebase or conflict fix:

```bash
git merge-base HEAD origin/master        # merge base
git merge-base --fork-point origin/master HEAD   # true fork, reflog-aware
git log --oneline $(git merge-base HEAD origin/master)..HEAD
```

`merge-base` is the common ancestor; `--fork-point` additionally reads
the reflog to find the original tip when master was rewound (squash
merges rewrite master constantly). Fork-point fails empty (exit 1) when
no reflog knows the old tip - fresh clones, post-`reset` states - so
always fall back:

```bash
git merge-base --fork-point origin/master HEAD \
  || git merge-base origin/master HEAD
```

Diff against the fork point, not against master's tip:
`git diff $(git merge-base HEAD origin/master)`. Three dots in
`git log A...B` also splits into theirs/mine/ours views.

## Fixing conflicts

When master moved into your branch's files (or CI shows conflicts):

```bash
git merge-base HEAD origin/master   # fork point
git merge origin/master             # merge now stops at conflicts
git status                          # conflicts: both modified / UU
# edit each file; keep BOTH sides when semantics differ; markers <<<<<<<,
# =======, >>>>>>> must be fully removed; no leftover marker may remain
git add <file>                      # per resolved file
git commit                          # closes the merge
```

The invariant: after resolution the file must build and behave as both
authors intended - not "master's version wins". Re-read the hunk after
editing. Then run the tests (the project's gates) BEFORE the merge
commit: a conflict resolution that compiles but breaks behavior is a new
bug with an innocent-looking commit. CI on the merge commit confirms.

`git rebase --continue` after conflicts follows the same resolve/stage/
continue loop when a rebase is the chosen path. Search for stray markers
across the tree before committing:
`grep -rn '^<<<<<<<\|^=======$\|^>>>>>>>' --include='*' .`

## Worktrees

Worktrees only when parallel work is genuinely in flight (two agents or
a fix interrupting a feature). One worktree per branch, always inside
the project dir:

```bash
git worktree add .worktrees/<branch-short-name> -b <type>/<desc>
# hack there; master checkout stays at repo root for shared commands
git worktree remove .worktrees/<name>       # after merge (see below)
git worktree prune                          # if dir was hand-deleted
```

No nested repos, no worktrees outside `.worktrees/`, no long-lived
worktrees (they rot: stale branches, drifted deps, wasted disk). A
worktree shares the repo's object store but not untracked files - build
artifacts and `.env` do not carry over.

## After a PR merges (cleanup)

The user merges the PR (never the agent, see below). The moment it
lands:

```bash
git checkout master
git pull origin master
git worktree remove .worktrees/<name>   # FIRST if one existed for it:
                                        # branch -d refuses a branch that
                                        # is checked out in a worktree
git branch -d <merged-branch>        # -d refuses unmerged, safe
git remote prune origin
git worktree prune
```

Under squash-merge this `-d` refuses EVERY merged branch: the squash
commit has a new SHA, so the branch still reads as unmerged. The merge
is proven by the PR record, not by git ancestry (`git cherry` marks
every branch commit `+` even after a clean squash merge - that output
is not evidence of pending work). Prove content parity with an empty
diff, then force-delete:

```bash
git diff master <branch> --stat   # must print NOTHING
git branch -D <branch>
```

Never `-D` without the empty diff - it is the only guard left. An
intervening merge on master makes the whole-tree diff non-empty; then
scope the diff to the paths your branch touched.

Repeat the start-of-work sweep to catch older debris. Then start the
next branch from the refreshed master. Never reuse a merged branch for
new work: squash-merge gives the new commits new SHAs, and a reused
branch pushes on top of a history that no longer matches - force-push
temptation follows.

### When the agent's terminal gates git mutations

If the shell refuses git mutations (a safety hook), hand the post-merge
cleanup to a helper running in a checkout of THIS repo at a commit that
exists on a merged ref. Cleanup instructions referencing a ref the
helper cannot see read as errors and push it to refuse or fabricate. A
helper refusing on those grounds is doing the right thing - fix the ref
scope, not the refusal.

## Agent state dirs are untracked

Every project dir accumulates agent state dirs - the running agent's
dot-dir and its kin (`<agent>/`) - used for WIP notes, plans, locks,
and session artifacts. They stay machine- and agent-local by design:
commits, diffs, and cleanup sweeps leave them alone. Ignore every
active agent's dir in the repos you touch:

```bash
printf '%s\n' '<agent>/' >> .gitignore   # one line per agent the repo carries
```

An earlier commit that already tracks one untracks the files without
deleting them: `git rm -r --cached '<agent>'` then commit. For shared
repos the contract lives at the repo level: `.gitignore` speaks to
every contributor and agent, while `.git/info/exclude` silences only
your clone.

**Contract and mission md files are agent-local too: every contract,
lane, mission, or spec md a worker or the agent writes lives in the
agent's state dir (`<agent>/`) inside the project.** Lane logs, mission
files, post-merge notes, spike decisions - all in there. Move anything
that landed in the repo tree or repo root to the state dir before the
PR opens.

## Human merges, agent assists

- The agent opens PRs, fixes, updates, and **stops at "ready"**: PR
  description current, checks green, no unresolved review threads.
- **Never merge a PR yourself.** Never call `gh pr merge`, never click
  merge, never bypass a red check. Merge is the human gate: a person
  decides what enters master. If the user says "merge it", confirm once
  - the user merging in the UI is fine; the agent running the merge
  command is not.
- On a red check: fix, push, watch again. On a stale PR: refresh
  (merge master in), push, re-watch.
- Report state, not confidence: "CI green, ready to merge" with the
  checks line pasted.
