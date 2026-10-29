# Repo maintenance patterns

Maintainer-only procedures for repo upkeep. Load when combining PRs or
syncing install-only content deltas.

## Combined PR pattern

When multiple open PRs target the same skill family, merge into one branch from origin/master:
1. `git checkout -b combined/<topic> origin/master`
2. `git diff origin/master..<pr1-branch> -- skills/ | git apply --3way`
3. `git diff origin/master..<pr2-branch> -- skills/ | git apply --3way`
4. Resolve conflicts (keep one copy of duplicated sections)
5. Close old PRs with `--delete-branch`; create single combined PR

## Install delta sync pattern

To sync content from ~/.agents/skills that diverged from repo:
1. Export origin/master tree: `git archive origin/master skills | tar -x -C /tmp/master-skills`
2. Normalize both sides (em-dash -> hyphen) and diff install vs master per skill
3. Filter style-only diffs (em-dash, description wording, first-person headers)
4. Keep install-only content deltas (new sections, rules, procedures)
5. Apply deltas onto clean master branch; push as single PR
