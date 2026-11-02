# Integration tests

Use this with `fluent-stage-tests.md` when adding Go integration tests.

## Scope

Integration tests verify component interactions with real dependencies.

Use integration tests for:
- databases
- queues and streams
- service components
- repository/storage behavior
- HTTP handlers and rendered responses
- dependency behavior that a unit test on public input and output cannot verify

## Rules

- Directory: `test/integration/`.
- Package: `package integration_test`.
- Always use a file pair: `*_test.go` for scenarios and `*_stage_test.go` for the stage.
- Do not use build tags.
- Dependencies run in Docker Compose.
- Tests run on the host and connect to exposed ports.
- Use the repository runner, usually `just` or `make`.
- Clean up external resources and compose state.
- Do not use testcontainers as the default.
- Do not use mocks for integration coverage.
- Follow `fluent-stage-tests.md` for scenario shape: one `Test*` per case, one `given` / `when` / `then` block ideally, `a*` methods in `given`, behaviour-named `-ing` methods in `when`, assertions in `then`.
- The tier changes only the `given` methods. Integration `given` methods start and prepare the real dependencies. The `when` and `then` shape stays the same as in E2E.

## Commands

Prefer existing project commands. Typical shape:

```bash
<runner> test-integration
```
