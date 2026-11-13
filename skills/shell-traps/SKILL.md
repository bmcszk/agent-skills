---
name: shell-traps
description: Use when writing or debugging shell scripts, pipelines, or compound command chains - verified traps a strong model misses, each of which exits 0 or silently matches nothing while the script looks fine.
license: MIT
metadata:
  audience: developers
  workflow: scripting
  category: dev
  technologies: bash, zsh, coreutils
---

# Shell traps

Each trap below was verified live: the script exits 0 or prints
nothing while doing the wrong thing.

- `awk` is byte-based under mawk: emoji regexes silently match zero
  lines. Pre-filter with `grep` or move the step to `python3`.
- `grep "$pattern"` with a dash-prefixed variable swallows the
  pattern as flags. Pass `--` before the pattern.
- `PIPESTATUS` is consumed by each assignment: capture all codes in
  one array assignment, not one variable per read.
- Emoji variation selectors break `=~` matching. Use
  `grep -qF -e` with a list of exact strings instead.
- `make` and `just` pre-parse recipe lines: heredocs and backslash
  continuations inside a recipe corrupt before the shell runs.
  Pipe through `printf` or call a script file, and run `just --list`
  after renaming recipes.
- Bare `timeout` on a script returns 126: pass the interpreter
  (`timeout 10 python3 script.py`).
- `sed -i` with a pattern that matches nothing exits 0 and changes
  nothing. Write patterns against actual file content, then
  grep-assert the landed token.
- `git mv` flatten-plus-overwrite keeps the OLD index content: after
  moving onto an existing path, diff the index, not the worktree.
- Multi-line commit messages go through a file (`git commit -F`),
  never `-m` with escaped newlines; same for `gh --body`.
- `pkill -f` matches the probe's own command line. Bracket one
  character (`pkill -f "[s]erver"`) to exclude the probe.
- Importing a script runs its module-level code: write every input
  file the consumer reads before launching it, not after.
- Tilde never expands after `=`; write `$HOME` in assignments.
- Hyphenated python package directories fail import with no hint:
  import errors from a hyphenated dir are a directory-name bug.
- Sourced env files set nothing exported: run `set -a` before
  sourcing (or `export` after) or downstream processes see nothing.
- A casual `git stash` inside a compound chain relocates untracked
  work mid-chain; stash by name and inspect `stash show` before
  popping.
