# Merge, rebase, and conflict resolution procedures

Read this when a merge or rebase stops on conflicts, when choosing
between merge and rebase for a refresh or a cleanup, or when a
conflict resolution needs proving before it becomes a commit. The
SKILL.md body carries the laws: merge is the default refresh, rebase
is deliberate, pushed history rewrites go back with
`--force-with-lease`. This file carries the procedures and the tool
semantics underneath them. The conflict-path semantics below
(inventory codes, refusals, marker gates, rerere, recovery) were
verified against git 2.56 in a sandbox with exact quoted wordings;
the refresh and rebase recipes follow the body's proven flow.

## Choosing merge or rebase

Decide by who can see the branch, never by taste:

| Situation | Move | Why |
| --- | --- | --- |
| Branch fell behind master, work is unpushed | merge from `origin/master` | ordinary push stays valid, nothing to rewrite |
| Branch is pushed and CI or others built on it | merge from master only | rewriting pushed commits orphans every checkout and CI run off the old SHAs |
| Local history needs cleanup before a PR opens | interactive rebase of UNPUSHED commits only | rewriting unpushed history costs nothing |
| Push was rejected because master moved | rebase the unpushed commits onto the new base, or merge | both work, merge needs no force ever |
| Conflicts ahead and the branch "could be rebased to dodge them" | resolve instead | a rebase replaces one conflicted resolution with one per replayed commit |

The audit-trail argument cuts the other way in this house: PRs are
squash-merged, so master history is linear by construction and a
merge commit on a feature branch records an integration event nobody
reviews. Prefer merge for safety, rebase for private cleanup.

## Refresh procedures

The default refresh (fetch, merge, push) lives in the body. A
deliberate rebase of unpushed work only:

```bash
git log --oneline origin/master..HEAD   # inventory what rewrites
git rebase origin/master
git push --force-with-lease             # only if the branch was pushed before
```

Prove the inventory line prints ONLY commits this session authored
before any rebase. A commit someone else pushed to the branch is
shared history; the rebase stops until that fact changes the plan.
`--force-with-lease` fails when the remote moved since the last
fetch, which is the guard working. Fetch BEFORE the force push and
never between the check and the push.

## Conflict resolution loop

The loop is: inventory, understand, resolve, verify, commit.

1. Inventory every unmerged path and drive the list to empty. The
   porcelain codes: `UU` = both modified, `AA` = both added. `git
   commit` refuses while the list is non-empty:

   ```bash
   git status --porcelain
   git diff --name-only --diff-filter=U
   ```

   The refusal wording: `error: Committing is not possible because
   you have unmerged files.` (exit 128).

2. Understand each conflict before touching it. Read both competing
   changes with their commits, not just the hunk:

   ```bash
   git log --merge --oneline <path>   # exactly the two commits that collide
   git show HEAD -- <path>
   git show <their-commit> -- <path>
   ```

3. Resolve semantically. The correct resolution is the file both
   authors intended: either side, a combination, or something neither
   side wrote. "Accept current change" clicked without reading the
   incoming side is the classic resolution bug. When the two sides
   encode genuinely different designs, stop and ask: the conflict is
   a decision, not a text edit.

4. Edit, then prove the file carries no markers:

   ```bash
   git diff --check    # one line PER marker line, exit 2 = found, 0 = clean
   ```

   `exit 2` (not 1) is the "found problems" code, and clean checks
   print nothing. Gate on the pattern, never on a line count.

   Marker shapes (default style):

   ```
   <<<<<<< HEAD
   current side
   =======
   incoming side
   >>>>>>> <branch or ours/theirs label>
   ```

   The side labels VARY: a fresh merge labels `HEAD` and the merged
   branch; `git checkout -m` re-creates them as `ours`/`theirs`; an
   octopus merge labels temp file names (`<<<<<<< .merge_file_X`).
   Match on the `<<<<<<<` prefix, never on a branch name.

   With `merge.conflictStyle diff3` or `zdiff3`, a base section joins
   the block: `||||||| <base-id>` + the common ancestor's line +
   `=======`. The base answers "what did this line look like before
   either side touched it", usually the fastest route to the right
   resolution.

5. Stage each resolved file and run the project's gates BEFORE the
   commit. Gate the staged tree too, not just the worktree - a
   marker can slip into the index:

   ```bash
   git grep --cached -n '^<<<<<<<'   # staged markers: exit 0 = found, 1 = clean
   ```

   Options come BEFORE the pattern: the option-after form dies with
   `fatal: option '--cached' must come before non-option arguments`
   (exit 128 on this git), turning the gate into a guaranteed crash.
   With `-e` the order frees up:

   ```bash
   git grep -n -e '^<<<<<<<' --cached
   ```

   The exit is inverted from intuition (grep semantics): 0 means
   markers ARE present. `git commit` (exit 128 refusal) plus this
   grep in CI is the pair that catches both accident classes.

6. Commit. A merge closes with `git commit`; a rebase continues with
   `git rebase --continue`. `--continue` refuses until every path
   from the current stop is staged:

   ```
   r.txt: needs merge
   You must edit all merge conflicts and then
   mark them as resolved using git add
   ```

Keep the resolution commit pure: it carries resolution and nothing
else. A refactor or a fix spotted mid-merge becomes its own commit
after the merge lands.

### rerere: reuse a recorded resolution

rerere records how one conflict was resolved and replays that
resolution when the identical conflict reappears: re-running an
aborted merge, the same refresh on a different lane, or a rescue
branch re-merge. It lives in gitconfig, so it is machine setup the
agent does not switch on at runtime (config rules: [setup.md](setup.md)).
With it enabled, a re-merge prints:

```
Resolved 'k.txt' using previous resolution.
```

Two behaviors a script must expect: the merge still exits 1 and
still demands a commit (auto-resolution is not a completed merge),
and the resolution lands in the worktree only, NOT the index
(`rerere.autoupdate` defaults false) - re-read it, `git add`, then
commit. `git rerere remaining` lists conflicts still
unresolved; `git rerere status` lists conflicted paths that hold a
recorded preimage in the current merge and empties once the
resolution is staged.

## Recovery paths

Abort when no merge is in progress errors with
`fatal: There is no merge to abort (MERGE_HEAD missing).` (exit 128),
so scripts gate it. The guard is silent but its exit is 1 when
nothing is in progress, 0 when the abort runs:

```bash
git rev-parse -q --verify MERGE_HEAD >/dev/null 2>&1 && git merge --abort
```

Wrap it when a strict 0 exit is required:

```bash
if git rev-parse -q --verify MERGE_HEAD >/dev/null 2>&1; then
  git merge --abort
fi
```

An aborted merge returns the branch to its pre-merge HEAD; edits made
during the conflict survive as worktree modifications - inventory
them before deciding they are garbage.

### Rescue branch mid-conflict

When a resolution has grown too good to abandon but the merge should
stop, carry the state to a side branch and keep the original branch
spotless:

```bash
git checkout -b rescue/<topic>     # works mid-conflict
```

`git switch -c` refuses mid-merge (`fatal: cannot switch branch while
merging`) - only `checkout -b` does this. The unmerged paths travel,
but `MERGE_HEAD` does not: the commit on the rescue branch is a plain
single-parent commit holding the resolved tree. Finish properly by
re-merging the incoming branch on the original branch afterwards -
with rerere enabled, the recorded resolution replays itself there.

### Repairing a botched resolution

Re-create the conflict from the index instead of restarting the
merge or wiping the file:

```bash
git checkout -m <path>             # markers re-appear, 3-way state restored
```

The inverse trap: `git restore --staged --worktree <path>` on an
unmerged path does NOT refuse - it silently resets the path to HEAD,
exit 0, destroying the incoming side with `MERGE_HEAD` still present.
An agent reaching for `restore` to "reset" a conflicted file loses
half the conflict with no warning; reach for `checkout -m` instead.

## Rebase-specific semantics

### ours and theirs flip meaning during a rebase

During a MERGE, `--ours` is HEAD (the branch merged into) and
`--theirs` is the incoming branch. During a REBASE they swap:
`--theirs` is the commit BEING REPLAYED (your own work), `--ours` is
the new base the commits land on. Resolving a rebase conflict with
merge instincts keeps the wrong side. `git status` during the stop
names the commit being applied - read it before trusting the flag:

```bash
git checkout --ours <path>    # merge: keep HEAD side | rebase: keep the new base
git checkout --theirs <path>  # merge: keep incoming   | rebase: keep your replayed commit
```

Neither form changes the index: the path stays `UU` until `git add`.
A rebase stop behaves like a merge stop otherwise - same inventory,
same markers, same gates. `git rebase --abort` returns to the
pre-rebase HEAD.

## Squash merge and octopus

`git merge --squash <branch>` stages the branch's combined diff as
one uncommitted change and prints `Squash commit -- not updating
HEAD`: no merge commit, no `MERGE_HEAD`, so the guarded-abort test
reads "no merge in progress". Discarding the staged squash:

```bash
git restore --staged --worktree .   # unstage everything, reset paths to HEAD
```

Finalize explicitly with `-m` or `-F`: a bare `git commit` opens an
editor pre-filled from `.git/SQUASH_MSG` with every squashed commit's
message, which dead-ends a non-interactive run.

An octopus (`git merge a b c`) with clean branches succeeds and
creates one merge commit with one parent per head. It does not refuse
cleanly on conflict: past the simple-merge fast paths it goes
non-atomic and can leave `UU` conflicts mid-fleet (its marker labels
are temp file names). Resolve multi-branch integrations one merge at
a time instead.

`MERGE_HEAD` holds one line per merged head and exists only while a
merge is uncommitted; in an octopus read it only in that state (`git
merge --no-commit` for a preview).

## Finding the common base, and views at the fork

`merge-base` is the common ancestor; `--fork-point` additionally reads
the reflog to find the original tip when master was rewound (squash
merges rewrite master constantly). Fork-point fails empty (exit 1) when
no reflog knows the old tip - fresh clones, post-`reset` states - so
always fall back:

```bash
git merge-base HEAD origin/master        # merge base
git merge-base --fork-point origin/master HEAD   # true fork, reflog-aware
git merge-base --fork-point origin/master HEAD \
  || git merge-base origin/master HEAD
git log --oneline $(git merge-base HEAD origin/master)..HEAD
```

`git log --oneline --left-right master...branch` splits the range
into sides: `<` = on master only, `>` = on the branch only. Three
dots = symmetric difference against the fork point (commits
reachable from both sides drop out); two dots `master..branch` lists
the branch's side only. Diffing the branch's committed changes
against the integration base takes the fork point as the FIRST rev
and HEAD as the second: `git diff $(git merge-base HEAD
origin/master) HEAD`. The single-rev form `git diff <commit>` diffs
against the WORKING TREE, so uncommitted edits count as branch
changes.

## Porting intent across branch families

The same feature often lives as parallel families of branches
(per-release, per-environment), and porting to one family is not
porting to all. Map the families first with `git for-each-ref` plus
merge-base ancestor walks: two branches sharing a recent merge-base
ancestor are one family, and a fix ported into one reaches the other
through their merge, not through a second port.

Port the FINAL diff, not the commit list: the commit list carries
fixup and rebase residue that cherry-picks as conflicts, while the
final diff is the settled intent. Apply it as one patch, then grep
the destination family for the feature's key symbols - a port can
silently drop a helper, a constant, or a test when a hunk applies
with fuzz, and the grep is the only check that catches the dropped
piece before the family merges.
