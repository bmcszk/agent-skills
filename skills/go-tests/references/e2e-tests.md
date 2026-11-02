# E2E tests

Use this with `fluent-stage-tests.md` when adding Go E2E tests.

## Scope

E2E tests verify complete user or service workflows across the running stack.

Use E2E tests for:
- API contracts through the real application
- multi-service workflows
- behavior that depends on deployed service wiring

## Rules

- Directory: `test/e2e/`.
- Package: `package e2e_test`.
- Always use a file pair: `*_test.go` for scenarios and `*_stage_test.go` for the stage.
- Do not use build tags.
- Services run in the project's full-stack runtime (for example Tilt or a deployed stack).
- Tests run on the host and connect to exposed ports.
- Use the repository runner, usually `just` or `make`.
- Clean up external resources.
- Do not use Docker Compose as the E2E orchestration default.
- Do not use mocks for E2E coverage.
- Follow `fluent-stage-tests.md` for scenario shape: one `Test*` per case, one `given` / `when` / `then` block ideally, `a*` methods in `given`, behaviour-named `-ing` methods in `when`, assertions in `then`.
- E2E `given` methods wait until the stack answers (`serviceIsReady()`). They do not start dependencies.
- HTTP-only E2E tests do not validate browser behaviour. For a frontend feature, add a browser test: [../../go-browser-tests/SKILL.md](../../go-browser-tests/SKILL.md).

## Commands

Prefer existing project commands. Typical shape:

```bash
<runner> test-e2e-up
<runner> test-e2e-run
<runner> test-e2e-down
<runner> test-e2e
```
