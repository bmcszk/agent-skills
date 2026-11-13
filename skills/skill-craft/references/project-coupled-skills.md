# Project-coupled skills: relocation and the skills CLI traps

Read when moving project knowledge out of a shared skills library,
or when installing and updating skills through the `skills` CLI.

## Relocation procedure

1. Grep both trees (the skill and the owning repo) for repo-prefixed
   paths, and judge coupling by content, not by skill name: a
   generically named skill can carry one repo's whole workflow.
2. Move project knowledge into the owning repo where its consumers
   live: docs, build recipes, agent instruction files.
3. Lessons that hold at the class level (every repo of that kind)
   become an umbrella reference in the generic skill.
4. The skill shrinks to a pointer: its body routes to the repo docs
   and carries only the class-level law.
5. Archive the removed material (git history counts); never `rm`.
   Verify every transplanted file exists at its destination before
   deleting the last copy.

## The skills CLI traps

- Discovery stops at root `skill/SKILL.md`: family-nested installs
  are invisible to the CLI while plain installs flatten, so the same
  skill can exist in both shapes and only one is updatable.
- Manifest keys must be leaf-only: a namespaced key never satisfies
  a present-check, and the CLI reinstalls that entry forever.
- A dry run that fails with a no-GitHub-metadata error is cured by
  the positional install form, not by editing metadata.
- Install refuses by NAME across all scanned agent trees, so
  `--force` overwrites a foreign copy of a same-named skill from a
  different source. Check the target's origin before forcing.

## Frontmatter health

The loader silently tolerates broken YAML: a skill with unparseable
frontmatter loads as if its description were empty and drops out of
routing without any error. Re-parse the whole tree with
`yaml.safe_load` after any frontmatter edit; a linter green is not a
parse proof.
