# GitHub review rounds via gh CLI

Read when a PR carries reviewer comments: gathering ALL of them,
knowing each one's exact code context, replying per thread, and
resolving the threads that are addressed and green. The conflict loop
a fix rides lives in
[merge-rebase-conflicts.md](merge-rebase-conflicts.md); the SKILL.md
body carries the reviewer-round laws (unanswered-thread count,
addressed-and-green resolution) and the one-fix-one-commit rule.

`gh` is the porcelain: `gh pr`, `gh run`, `gh repo` for the lifecycle
you would click, `gh api` for everything porcelain does not shape
(review-comment lists, thread state, mutations). Preflight once per
session: `gh auth status`. The REST and GraphQL query forms below
were probed live on real repos; the reply, files-list, and pagination
patterns follow established house procedure from real review rounds
and carry their known failure modes verbatim.

## The comment surfaces

| Surface | Where reviewers write it | Fetch |
| --- | --- | --- |
| Inline thread | on a diff line during review | REST `pulls/N/comments` |
| Review summary | one review body, no anchor | `gh pr view --json reviews` |
| Conversation | on the PR timeline, not the diff | REST `issues/N/comments` |
| Thread state | resolved/outdated flags | GraphQL `reviewThreads` only |

Full inventory (REST, paginated; collection endpoints default small
pages and walk every page with `--paginate` when the PR accumulates
more entries than one page holds):

```bash
gh api "repos/O/R/pulls/N/comments?per_page=100" --paginate \
  --jq '.[] | {id, user: .user.login, path, line, original_line,
               side, start_line, in_reply_to_id, commit_id}'

gh api "repos/O/R/issues/N/comments?per_page=100" --paginate \
  --jq '.[] | {id, author: .user.login, body}'

gh pr view N --json reviews,latestReviews,reviewDecision,headRefOid
```

Thread state plus the last replies per thread (GraphQL):

```bash
gh api graphql -f query='
query{repository(owner:"O",name:"R"){pullRequest(number:N){
reviewThreads(first:100){totalCount nodes{
id isResolved isOutdated viewerCanResolve viewerCanUnresolve
comments(last:5){nodes{databaseId body author{login}}}}}}}}' \
  --jq '.data.repository.pullRequest.reviewThreads.nodes[]
        | {thread: .id, isResolved, isOutdated,
           canResolve: .viewerCanResolve,
           canUnresolve: .viewerCanUnresolve,
           dbs: [.comments.nodes[].databaseId]}'
```

Join REST to GraphQL by `databaseId`: REST lists the comments, GraphQL
tells you which thread each one belongs to and whether that thread is
resolved. A thread whose last comment is still the reviewer's (no
reply) is the "unanswered" set the completion gate counts.

## Code context per comment

Each inline comment carries its anchor:

- `path` + `line` + `side`: the flagged file and edge (`RIGHT` = new
  code, `LEFT` = old). `start_line` is set for range comments.
- `body` and `diff_hunk`: the comment text and the surrounding diff
  window, enough to read the neighborhood without opening the repo.
- `commit_id`: the PR commit the comment anchored to.
- `original_line` / `original_commit_id`: the anchor at the moment of
  commenting.

The outdated signature is `line: null` with `original_line` set: the
PR head moved since the comment landed, so `line` no longer resolves.
Such a thread needs the NEW location found and named in the reply -
reviewers reading only the thread see stale code and conclude nothing
was fixed. Anchor into the real file at the commented commit when the
context matters:

```bash
git rev-parse HEAD                          # local head to compare
gh api "repos/O/R/pulls/N/files?per_page=100" --paginate \
  --jq '.[] | {filename, status}'           # what the PR touches
gh api "repos/O/R/contents/<path>?ref=<anchor-sha>" \
  -H "Accept: application/vnd.github.raw" > /tmp/anchored-file
```

The raw form returns the file bytes; without the `Accept` header the
payload is a JSON object carrying base64 `content`. Verify the remote
before writing a fix: `gh pr view N --json headRefOid` must equal
`git rev-parse HEAD` - local state is a hypothesis about the PR, not
a proof of it.

## Replying

Replies go to the replies endpoint of the TOP-LEVEL comment id. Reply
bodies travel as plain argv values, never stdin (`-f body=@-` under a
shell or Python wrapper can silently post an empty or literal marker
body):

```bash
gh api --method POST \
  "repos/O/R/pulls/N/comments/<top-level-comment-id>/replies" \
  -f body="Addressed in <full-head-sha>: <what changed and why>"
```

- Replying to a reply (a comment that itself has `in_reply_to_id`)
  fails: only top-level ids accept replies.
- One `gh api` argument binds one key: `-fcommit_id=<sha>
  -fpath=<p>` when several fields are needed; space-separated
  `-f commit_id X` dies with `accepts 1 arg(s), received...` (the
  count tracks however many stray words were left over).
- Verify by LISTING, never by re-GETting the single id: list
  `pulls/N/comments` after a batch and confirm each returned id, and
  read the served body back with
  `gh api repos/O/R/pulls/N/comments/<id>`.

Body as JSON for scripted batches - write the file, pass
`--input <file>`:

```bash
gh api --method POST "repos/O/R/pulls/N/comments" \
  --input reply.json
```

## Resolving threads

Resolution is GraphQL-only. Resolve when the thread is truly
settled:

```bash
gh api graphql -f query='
mutation{resolveReviewThread(input:{threadId:"<GRAPHQL-thread-id>"}){
thread{id isResolved}}}'

gh api graphql -f query='
mutation{unresolveReviewThread(input:{threadId:"<id>"}){
thread{id isResolved}}}'
```

Procedure: reply first, resolve after - a resolved thread collapses
and a reviewer reading it may miss an answer posted after the fact.
The flag flip is the proof: after the mutation, list the threads
again and confirm `isResolved` flipped on the matching id (`viewerCanResolve`
from the thread query tells you whether the token may resolve that
thread at all). A bogus id fails with `Could not resolve to a node
with the global id of '...'` (`type: NOT_FOUND`). The resolution
timing - addressed AND green - is the body's law; the spot check is
`gh pr checks N` on the head the replies cite.

Answers that reference the fix carry the full head SHA. Fetch it:

```bash
gh pr view N --json headSha --jq .headSha
```

A short SHA (`abc1234`) is not a valid anchor when a POST wants the
commit - use the full SHA.

## Thread pagination

`first: 100` covers everything a normal PR accumulates. Past that,
GraphQL pages by cursor:

```bash
gh api graphql -f query='
query($after:String){repository(owner:"O",name:"R"){pullRequest(number:N){
reviewThreads(first:100, after:$after){pageInfo{hasNextPage endCursor}
nodes{id isResolved isOutdated
comments(last:5){nodes{databaseId body}}}}}}}' \
  -F after="$cursor"
```

REST pages the same way with `--paginate`, or by hand:

```bash
gh api "repos/O/R/pulls/N/comments?per_page=100&page=2"
```

## The completion gate

The round is done when every surface agrees with the story:

- Zero unanswered threads: GraphQL `reviewThreads` shows no
  `isResolved: false` thread whose last comment is a reviewer's. Each
  either resolved (fix landed, replies in, checks green) or visibly
  open with the reply that argues why.
- Remote proof, not local belief: `gh pr view N --json headRefOid` ==
  `git rev-parse HEAD`, and the fixed content is visible in the
  served patch (`repos/O/R/pulls/N/files --paginate`). "I pushed
  earlier" proves nothing: a refused or no-op push leaves the
  reviewer on stale code while the reply claims otherwise.
- `gh pr checks N` all pass; `reviewDecision` may still read
  CHANGES_REQUESTED - only the human re-review flips that, and that
  is the plan, not a failure.

Wrap every remote read in a retry (3 attempts, short sleep): a single
`dial tcp ... i/o timeout` against api.github.com is routine and is
never news about your PR.

## Authoring the PR body

- The body is current with the branch: update it in the same push
  cycle as the work. When later epics absorb into an already-open PR,
  add one section per absorbed item with a one-line result and the
  commit refs. A reviewer judges completeness by the body, so a stale
  body reads as an unfinished PR even with CI green.
- Close with a gate-evidence block naming every gate the repo enforces
  (build, vet, lint issue counts, full test count) plus the CI
  conclusion, each quoted from a rerun at the head SHA. An omitted
  gate reads as hidden work, and numbers from an older slice log are
  not evidence.
- A grouped-feature PR opens with one line per feature (the feature
  and its one-line result), followed by the shared design decisions
  (parity policy, recorded deviations, fail-closed guarantees) and the
  gate-evidence block for the whole branch. The title comes from the
  lead feature; the remaining feature titles live in the body list.
  One grouped PR gets one review sweep covering every feature, with
  each finding checked against its own feature's contract.
- A partial feature is disclosed: mark it in the title or drop it from
  the title, and state the deferral in the body. A title claiming a
  partial feature reads to a skim-reader as shipped.

## Pre-open audit

Open the PR only after a read-only audit over the diff and the body
draft, in this order:

1. Re-read every doc the body links (verification docs, acceptance
   tables, appendices) against the final tip, and fix stale docs
   before touching the body: a stale-doc contradiction is the most
   common blocking finding.
2. Diff-verify the body's file and scope claims: check every path the
   body names against `git diff <base>...HEAD --name-only`. A body
   naming a file the diff does not touch, or missing one it does, is a
   standing reviewer finding.
3. Re-run the gates at head: build, vet, formatting, full tests, the
   repo's lint script, and any environment-gated smoke with the
   environment the tests expect.
4. Re-verify the gates after any fix round, then run `gh pr create`.
