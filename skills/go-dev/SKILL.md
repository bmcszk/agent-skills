---
name: go-dev
description: >-
  Use for any Go implementation, refactor, code review, or Go version bump.
  Holds the Go decision order and hard rules, and routes to references for
  core style and design rules, tradeoffs, and modern Go (1.24 to 1.27 APIs,
  go fix, json/v2). For tests, also load go-tests. For a new project, load
  go-setup.
license: MIT
metadata:
  audience: developers
  workflow: development
  category: backend
  technologies: go
---

# Go development

Go policy and router. Keep this file loaded for any Go work. Load only the reference that matches the task.

## Decision order

When rules conflict:

1. Safety and correctness.
2. Hard rules of [coding-rules](../coding-rules/SKILL.md) and this skill.
3. Repo consistency. Follow the patterns of the repo and its sibling services, even if a generic shortcut is shorter.
4. Good practices, when the repo has no local pattern.
5. YAGNI. The smallest readable change within the above.

Minimalism cuts invented complexity. It does not override the hard rules. Mark a deliberate shortcut with a known limit as `// ponytail: <limit>; <upgrade path>`. Details are in [references/development-balance.md](references/development-balance.md).

## Hard rules

- Match repo patterns before you add new ones.
- Wrap errors with `%w`. Use `errors.Is` and `errors.As`. Pass `context.Context`.
- Define interfaces at the consumer. No separate `interfaces.go` files.
- Do not add compile-time interface asserts (`var _ Interface = (*Type)(nil)`) or `var _ = ...` blocks that keep symbols or imports alive. Real call sites and tests catch breakage, and the `unused` linter then names real dead code.
- Use `errgroup` with `SetLimit` for goroutines that can fail.
- No mocks in unit tests. Test dependency behaviour with integration or E2E tests.
- No `//nolint` or `//revive`. Fix the cause.
- No speculative abstractions, packages, or dependencies.
- Never use a stdlib API newer than the `go` directive in `go.mod`.
- If you find a bug, record it before you patch it.
- Declaration order: load [coding-rules](../coding-rules/SKILL.md) File structure when editing `.go` files.

## Design acceptance is a gate

Build, vet, lint, and tests check that code is correct. None of them checks that the user accepts the design. Before you apply a structural change (file layout, struct shapes, DSL patterns) to many files, get the user's sign-off on one probe file. If the user says the shape is wrong, re-read the rule from scratch instead of re-applying the stored one.

## References

| Task | Read |
|------|------|
| Any tradeoff | [development-balance.md](references/development-balance.md) |
| Implementation, refactor, or review | [core-go-rules.md](references/core-go-rules.md) |
| Go version bump, `go fix`, new stdlib API, json/v2, omitempty/omitzero | [modern-go.md](references/modern-go.md) |
| Unit, integration, or E2E tests | [go-tests](../go-tests/SKILL.md) |
| New project, layout, library choice | [go-setup](../go-setup/SKILL.md) |
| File layout (const/var/types/public before private) | [coding-rules](../coding-rules/SKILL.md) |
