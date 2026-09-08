# Setup

One-time steps per machine and per project. Run once, then never again.

## Install the beans CLI

```bash
brew install hmans/beans/beans
# or
go install github.com/hmans/beans@latest
```

Repo: <https://github.com/hmans/beans> (760+ stars).

## Initialize a project

```bash
beans init
```

Creates `.beans/` directory and `.beans.yml` config. Commit both to
version control.

## Agent integration

Add to `AGENTS.md`, `CLAUDE.md`, or equivalent:

```markdown
**IMPORTANT**: before you do anything else, run the `beans prime` command and heed its output.
```

## OpenCode plugin

Copy `.opencode/plugin/beans-prime.ts` from the Beans repo to your
project's `.opencode/plugin/` directory.

## Configuration (`.beans.yml`)

`beans init` writes a default `.beans.yml`. Edit it when you want to
override the defaults; commit the file alongside `.beans/`. All keys
are optional.

```yaml
project:
  name: my-project
beans:
  path: .beans
  prefix: myproj-        # Prefix for bean IDs (e.g., "myproj-a3x1")
  id_length: 4            # Random ID suffix length
  default_status: draft   # Every new bean is research-first
  default_type: task
worktree:
  base_ref: origin/main
  integrate: pr
agent:
  enabled: true
  default_mode: act
```

Notes:

- `beans.default_status` is what the skill workflow model expects (`draft`).
  Don't change it to `todo` unless you're skipping triage — that's the
  process violation documented in **Closure gates (binding)** in the
  parent `SKILL.md`.
- `beans.prefix` shows up in every ID; pick something short and stable.
- `worktree` and `agent` blocks are only relevant when `beans serve`
  or the agent workflow is in play — safe to leave at defaults.
