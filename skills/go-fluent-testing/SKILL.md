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

## Extremely important — Given/When/Then roles

Hard rules for **every** tier (fluent and classic):

- **given** — set the stage only: initial state, dependencies, data.
  All setup must be explicit. **No asserts.** Not the action under test.
- **when** — usually a **one-liner**: trigger **only** what this test
  exercises. No asserts, no outcome checks, no validation.
- **then** — **all** asserts, expects, and outcome checks. Nothing else.

Assert helpers (e.g. `videoUploadedSuccessfully`) belong in **then**,
never chained under `given` or `when`. In **then**, assert the **when**
action and its outcomes — not setup already established in **given**.

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
  This blackbox rule applies to BOTH unit styles below.
- **No I/O**: no DB, no HTTP, no filesystem — mock every dependency
  via constructor injection (define a small interface at the consumer).
- **Speed** <10ms per test; **naming** `TestComponent_Scenario`.
- **Never**: `wantErr bool` (split into separate tests), build tags,
  `//nolint`, deleting or skipping tests.

## Unit styles: fluent OR classic

Unit tests accept two layouts — pick per repo convention, keep one per
repo, never mix within a package:

**Fluent** — the full DSL below (parts struct, `newParts(t)`,
`.and()` chaining). Use when the package already has a fluent DSL or
the tier is integration/E2E anyway.

**Classic** — plain test funcs segmented by `// given` / `// when` /
`// then` comments. Default for units: no DSL to build, same
discipline, less machinery. In FLUENT tests do NOT write these three
comments: the `given.`/`when.`/`then.` receiver already names the
phase, so a marker above it is narration (coding-rules comment rule;
confirmed as the standard in a triage where a repo-wide sweep counted
the markers as debt, not convention). The comments belong to the
classic style only, where nothing else marks the sections. Test-func
doc comments follow the same line: describe the non-obvious contract
under test (an invariant the name does not carry) — never restate the
given/when/then chain or the assertions below.

Timing and duration are part of a feature's contract: when the code
under test paces output (`interval_ms`, backoff, debounce), assert the
pacing (per-frame arrival deltas, total duration bounds) and exercise
durations that cross server-level limits (`http.Server` WriteTimeout),
not only millisecond-fast samples — a suite whose every stream finishes
in <100ms cannot see truncation at 10s. Also cover the server's own
documented env var and timeout knobs in at least one long-running e2e.
Wire-behavior features (streaming formats, delivery headers, retry
exhaustion) need at least one e2e assertion each, even when unit tests
already check the pieces — e2e proves the parts wired through the real
HTTP server, router wrappers, and middleware.

```go
func TestService_CreateUser(t *testing.T) {
    // given
    mockRepo := &MockRepository{}
    mockRepo.On("Save", mock.Anything, mock.Anything).Return(nil)
    service := service.NewService(mockRepo)

    // when
    err := service.CreateUser("test@example.com", "Test User")

    // then
    assert.NoError(t, err)
    mockRepo.AssertExpectations(t)
}
```

Classic rules: the three comments in order, one each; setup only under
`// given` (no assertions), calls only under `// when` (prefer one call
— the action under test; no assertions), assertions only under
`// then` (every assert lives here); no section skipped; state stays
local to the test func (the parts-struct rule does not apply here).

## Fluent pattern (integration & E2E; units when repo is fluent)

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

- `newParts(t)` returns `p, p, p` (given, when, then) over one flat parts
  struct that holds `*testing.T`, `require.New(t)`, and ALL test
  state — no local state variables in test funcs, no separate state
  structs.
- LARGE DSL SHAPE (settled after five rejected topologies): ONE flat `parts`
  struct holding ALL state — core (T, require/assert, ledger) PLUS every domain's
  fields. State never splits into per-domain structs; no wrapping composite
  fixture (rejected on sight); no per-domain wrapper structs either (rejected:
  `type <dom>Parts struct { parts }` markers added ceremony, deleted same day).
  Every builder is `func (p *parts) … *parts` in its domain file, so mixed
  chains and `.and()` survive with zero call-site churn. Self-typed generics
  (`parts[S]`) are NOT the fix for chain typing. They break cross-domain chains
  (Go 1.27 generic methods don't rescue this either: a `*parts` receiver cannot
  produce a sound domain-typed return; verified in scratch).
- ONE constructor: `newParts(t)` in the base file constructs the whole parts
  literal and returns `p, p, p`. Domain ctors per file are ceremony and are deleted.
  Never split construction or delegate partial construction, or core state
  stays nil.
- Pairs: each domain primary is an exact-stem pair `X_test.go` ↔
  `X_parts_test.go`; extra feature files inside a domain share the domain parts
  file. A parts file is a pure method group on `*parts` (no struct, no ctor of
  its own); a parts file with zero methods is deleted.
- NEVER base-embeds-domains while domains-embed-base — that cycle reads as a
  structural error. Recipe: `references/fluent-testing-guideline.md`.
- Renaming files to exact-stem pairs: `git mv` per file, then RE-CHECK that no
  other file still uses the old stem (`grep -rn old-stem *.go *.md`): renames
  leave stale doc references and duplicate stems (a file of the same domain
  name already existing) that gates never catch. Fold a small same-domain test
  file into its pair's primary rather than leaving two stems for one domain.
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

- NEVER use direct helper function calls inside fluent Test funcs —
  everything flows through given/when/then methods (classic units:
  setup under `// given` instead)
- NEVER assert or validate in `given` or `when` (classic: not under
  `// given` or `// when`; fluent: not on `given.` or `when.` chains)
- NEVER chain multiple actions in `when` unless the test truly
  exercises them as one unit — default is a **one-liner**
- NEVER put asserts outside `then` (classic `// then`; fluent `then.`)
- NEVER use build tags, `//nolint`, or skip/delete tests
- NEVER leave containers running or skip cleanup (integration/E2E)
