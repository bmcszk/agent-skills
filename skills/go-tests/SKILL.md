---
name: go-tests
description: >-
  Use when adding, changing, or reviewing Go unit, integration, or E2E tests
  or test stages, when choosing which test level a code change needs, when
  choosing between integration and E2E tests, when writing a benchmark or an
  Example, when reading a coverage report, or when picking the test runtime.
  Covers unit tests for pure public functions, integration tests on Docker
  Compose, and E2E tests on the project's full-stack runtime, all in the fluent
  given/when/then stage pattern (*_test.go plus *_stage_test.go).
  Browser tests: see go-browser-tests.
---

# Go tests

Go unit, integration, and E2E tests. These conventions are required. Do not swap them for a shorter generic approach.

Shared Go rules are in [../go-dev/SKILL.md](../go-dev/SKILL.md).

## Choose the level

Choose by behaviour, not by convenience.

| Level | Use for | Runs on | Read |
|-------|---------|---------|------|
| Unit | Pure public functions: validation, parsing, mapping, formatting, deterministic calculations, simple business rules | No services | [unit-tests.md](references/unit-tests.md) |
| Integration | Databases, queues, streams, storage, service components | Docker Compose | [fluent-stage-tests.md](references/fluent-stage-tests.md), [integration-tests.md](references/integration-tests.md) |
| E2E | API contracts, multi-service workflows, deployed service wiring | The project's full-stack runtime (for example Tilt or a deployed stack) | [fluent-stage-tests.md](references/fluent-stage-tests.md), [e2e-tests.md](references/e2e-tests.md) |

Runtime and command choice: [test-orchestration.md](references/test-orchestration.md).

More references, each with its load condition:

- Growing or splitting a stage, adding a stage file, or changing the stage type: [stage-structure.md](references/stage-structure.md).
- Test data, fake upstream servers, async checks, or test file layout: [test-data-and-config.md](references/test-data-and-config.md).
- Comparing implementations or input sizes, or writing a new benchmark: [benchmarks.md](references/benchmarks.md).
- Reading a coverage report or choosing which untested path to attack next: [coverage.md](references/coverage.md).
- A runnable `Example*` next to a public API: [examples.md](references/examples.md).
- Fuzzing a target, or faking time with `testing/synctest`: [unit-tests.md](references/unit-tests.md).

## Hard rules: unit

- At most one unit test file per source file. Name it after the file under test with a `_test.go` suffix (`foo.go` becomes `foo_test.go`). Not every source file needs a unit test. Do not dump tests for many source files into one test file.
- Blackbox tests in `package <name>_test`.
- A unit test feeds inputs and asserts outputs and errors on pure code. If the test needs a hand-written type that satisfies a production interface, write an integration or E2E test instead.
- Test only pure, easily testable functions, ideally public ones.
- Assert on direct inputs, outputs, and returned errors.
- Before handoff, run on new unit files in the diff (skip `test/integration/` and `test/e2e/`): `git diff --name-only --diff-filter=A origin/<default-branch> -- '*_test.go' | grep -vE '/test/(integration|e2e)/' | xargs rg --files-without-match '^package \w+_test$'`. Empty output means pass.
- One `Test*` function per outcome. Assert that outcome directly (`require.NoError`, `require.Error`, and the like).
- A table shares inputs for one outcome only. Put another outcome in its own `Test*` function.
- Mixed success/error table fields (`wantErr`, `wantError`, `wantFail`, and the like) bundle two outcomes in one row. Do not write them.
- Mark sections with `// given`, `// when`, and `// then`. **given** is explicit setup only (no asserts, not the call under test). **when** is usually one call under test. **then** holds all asserts.

## Hard rules: integration and E2E

- Integration tests live in `test/integration/` with `package integration_test`. E2E tests live in `test/e2e/` with `package e2e_test`.
- Always use a file pair. `*_test.go` holds scenarios. `*_stage_test.go` holds the stage.
- Use the fluent `stage`: `given, when, then := newStage(t)`. One `given`, one `when`, one `then` per test. **given** is explicit stage setup only (no asserts, no action under test). **when** is usually one `-ing` call under test. **then** holds all asserts. Do not blur phases; details in [fluent-stage-tests.md](references/fluent-stage-tests.md#given--when--then-roles).
- No build tags. No mocks. No `//nolint`. Never skip or delete a test to get green.
- Tests run on the host and connect to exposed ports. Clean up external resources with `t.Cleanup`, registered in the `given` method that creates them.
- Wire behaviour (streaming formats, delivery headers, retry exhaustion) needs at least one E2E assertion each, even when unit tests cover the parts. Only E2E proves the real server, router, and middleware are wired.
- When the code paces output (interval, backoff, debounce) or has timeouts, assert the pacing and test at least one duration past the server limits (for example `http.Server` `WriteTimeout`). A suite where every stream ends in 100 ms cannot see a cut at 10 s.
- Use the repo runner, usually `make` or `just`.

## Bugs found by tests

Do not patch first. Record the bug (what failed, how to reproduce) before you change code, then fix it with a test that fails first.
