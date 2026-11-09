# Gitignore contract

The repo-level `.gitignore` is the shared contract: it speaks to every
contributor and every agent in the repo. `.git/info/exclude` silences
paths in one clone only; the global `core.excludesFile` silences one
machine (see [setup.md](setup.md) for the config). A path that must be
invisible to the whole repo goes in the repo file.

## Baseline classes every repo carries

Group rules under short comment headers: build output, test artifacts,
runtime data, logs, env files, dependencies, agent dirs, OS noise.

```gitignore
# Build output
/bin/
/dist/
/build/
/hello                 # generated binary at repo root, anchored

# Test and coverage artifacts
*.test
*.out
coverage.out
coverage.html
/test-results/
e2e-*.png
cookies*.txt

# Runtime data and local stores
/data/
*.db
*.sqlite
*.sqlite3
saves/*.json

# Logs
*.log
*.pid

# Environment and secrets
.env
.env.local
.env.*

# Dependencies and caches
vendor/
node_modules/
.cache/

# OS and editor noise
.DS_Store
Thumbs.db
*.swp
*~
.idea/
.vscode/
```

Go repos additionally ignore `go.work` and keep `go.mod` + `go.sum`
tracked. Product lock files stay tracked; lock files belonging to
agent tooling inside the repo (`.opencode/package-lock.json`) follow
the tool dir and stay untracked.

## Agent dirs and worktrees

Agent state dirs and the worktree home stay untracked, one line per
dir the repo actually carries:

```bash
printf '%s\n' '.worktrees/' '.hermes/' '.pi/' '.opencode/' >> .gitignore
```

`.worktrees/` pairs with the worktree law in SKILL.md (worktrees live
only there). A trailing-slash dir rule also covers the contracts,
lane logs, and mission files an agent writes inside that dir, so no
file-level rules are needed for them.

## Write rules that survive contact

- Anchor generated binaries that share the product's name (`/hello`):
  unanchored `hello` also swallows a future directory of that name.
- Downloaded per-environment tool binaries (`bin/tailwindcss`,
  `custom-gcl*`) are ignored by path, never committed.
- Negations come after the broad rule they carve out of. House shape
  for keeping tracked fixtures under an ignored format:

  ```gitignore
  *.pdf
  !pkg/rag/parser/testdata/*.pdf
  ```

- Never blanket-ignore a format the test suite loads without such a
  negation: `git add` on the ignored fixture refuses with an
  "ignored by .gitignore" hint, and a force-add hides the landmine.
- Ignore whole generated directories (`/dist/`) instead of listing
  their artifacts file by file.
- Level owns the rule: product-wide classes in the repo file, one
  clone's personal scratch in `.git/info/exclude`.

## Verify after every edit

```bash
git check-ignore -v .worktrees/ .hermes/ .pi/ .opencode/
git status --short
```

`git check-ignore -v` prints the matching rule per path and exits 1
for a path no rule hits: every path meant to be ignored must print a
line. `git status --short` must show the ignored dirs gone from the
untracked list. For a negation, `git add` the fixture path and
confirm it stages.
