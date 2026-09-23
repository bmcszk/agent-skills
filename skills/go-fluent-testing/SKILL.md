---
name: go-fluent-testing
description: 'Go testing with the fluent Given/When/Then DSL across all test tiers: unit (mocks, blackbox), integration (testcontainers, real deps), and E2E (docker-compose, HTTP). ONE methodology — parts struct, newParts(t), .and() chaining, all state in parts. Canonical rules in references/fluent-testing-guideline.md. Use when writing or reviewing ANY Go test: unit, integration, E2E, or choosing the tier for a new test. Keywords: go test, fluent testing, given when then, parts struct, testcontainers, docker-compose, unit test, integration test, e2e test, testify, mocking, blackbox.'
license: MIT
metadata:
  audience: developers
  workflow: testing
  category: testing
  technologies: go, testify, testcontainers, docker-compose
---

## What I do

All Go testing — unit, integration, and E2E — in one fluent
Given/When/Then methodology. One DSL, one parts struct, three tiers.

## MANDATORY Reference

**ALL Go tests MUST follow:** `references/fluent-testing-guideline.md`
(included in this skill directory). It is the single source of truth
for the DSL: parts struct, `newParts(t)`, `.and()` at END of line,
all state in parts, no direct helper calls in Test funcs, t.Run
promotion, fixtures over inline strings.

## Choose the tier

| Tier | Directory | Package | Dependencies | Speed |
|---|---|---|---|---|
| **Unit** | next to code under test | `<name>_test` (external) | mocks only, no I/O | <10ms/test |
| **Integration** | `test/integration/` | `integration_test` | testcontainers (real DB/services) | 100ms–1s/test |
| **E2E** | `test/e2e/` | `e2e_test` | docker-compose services, HTTP on exposed ports | seconds/test |

Decision rule: test business logic through public APIs → **unit**;
test a component against a real dependency → **integration**; test a
complete user workflow or API contract across services → **E2E**.
Browser-checking a frontend needs chromedp — see the `go-browser-tests`
skill; migrating an existing suite — see the `go-fluent-test-migration`
skill.

## Unit rules (blackbox — CRITICAL)

- **Package** `<name>_test` (e.g. `handlers_test`); test ONLY exported
  functions/methods; never touch unexported fields or private funcs.
- **No I/O**: no DB, no HTTP, no filesystem — mock every dependency
  via constructor injection (define a small interface at the consumer).
- **Speed** <10ms per test; **naming** `TestComponent_Scenario`.
- **Never**: `wantErr bool` (split into separate tests), build tags,
  `//nolint`, deleting or skipping tests.

## Fluent pattern (all tiers)

```go
func TestService_CreateUser(t *testing.T) {
    _, when, then := newParts(t) // declare only used sections

    when.
        createUser("test@example.com", "Test User")

    then.
        noError().and().
        userPersisted()
}
```

- `newParts(t)` returns `p, p, p` (given, when, then) over one parts
  struct that embeds `*testing.T`, `require.New(t)`, and ALL test
  state — no local state variables in test funcs.
- Tier differences live in the given-methods only: unit `given` builds
  mocks; integration `given` starts containers; E2E `given` waits for
  compose services. The when/then shape is identical everywhere.

## Commands

```bash
# Use the project's runner (make or just)
<runner> test-unit         # unit only
<runner> test-integration  # integration only
<runner> test-e2e          # e2e only
<runner> check             # vet + test + lint
```

## Forbidden (all tiers)

- NEVER use direct helper function calls inside Test funcs — everything
  flows through given/when/then methods
- NEVER put validation in the when section
- NEVER use build tags, `//nolint`, or skip/delete tests
- NEVER leave containers running or skip cleanup (integration/E2E)
