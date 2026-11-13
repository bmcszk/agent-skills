# Hermes-local skills

Read when authoring or editing a skill under ~/.hermes/skills, or
when deciding where knowledge belongs in the two-layer setup.

## Layering

- Global skills (~/.agents/skills, the bmcszk/agent-skills repo) are
  the source of truth: generic, agnostic knowledge any install
  needs. Hermes loads the directory as an external skill root and
  global outranks hermes on any conflict.
- Hermes skills (~/.hermes/skills) carry only the non-generic
  residue: machine-local paths, project-specific procedures, and
  session laws tied to this install. Nothing hermes-side lives in a
  repository, so a hermes skill is unrecoverable once deleted:
  treat it as disposable, or promote it to global first.
- Before writing anything hermes-side, check the global skill of the
  same topic. Restating global content is duplication that drifts:
  write a pointer line instead.

## The notes pattern

Local knowledge attaches to a global skill as a hermes notes skill
(`<skill>-notes`, e.g. `go-dev-notes` beside global `go-dev`):

- The notes skill opens with a pointer: load the global skill
  first; this file adds only what the global one must not carry.
- Notes hold the local residue - repo names, lane paths, worker
  plumbing, one machine's quirks. No restatement of the global
  body, and no generic knowledge: what passes the knowledge delta
  test on a second project belongs in a global PR.
- When notes knowledge proves generic, promote it: PR it into the
  global skill's reference set, delete the hermes copy, leave the
  pointer.
- The global skill's body carries the matching pointer line (when
  to load the notes skill), so the load path works from both sides.

## Naming

- Keep hermes and global names distinct, except the paired
  `<skill>-notes` form: a same-name local copy invites silent
  shadowing.
- A hermes description states the local trigger (use when <this
  install's condition>); global descriptions stay agnostic.
