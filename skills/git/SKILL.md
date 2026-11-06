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
is safe as written. Verify nothing else claims the name: `git branch -a
--list <type>/*` and `git ls-remote --heads origin <type>/*`. Never
branch from another feature branch unless the work depends on it; if it
does, name the base branch in the PR description.

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

Repeat the start-of-work sweep to catch older debris. Then start the
next branch from the refreshed master. Never reuse a merged branch for
new work: squash-merge gives the new commits new SHAs, and a reused
branch pushes on top of a history that no longer matches - force-push
temptation follows.

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
