# Test orchestration

Use this to choose the runtime environment for Go test work.

## Unit

- No external services.
- No mocks, stubs, fakes, or spies.
- Verify public, deterministic behavior with direct inputs, outputs, and returned errors.
- Read `unit-tests.md` for detailed shape.

## Integration

- Use Docker Compose for real dependencies.
- Tests run on the host and connect to exposed ports.
- Prefer the repository runner: `make`, `just`, or existing scripts.
- Clean up Compose state after tests; use `down -v` for throwaway integration stacks.
- Do not use testcontainers as the default.
- Read `integration-tests.md` and `fluent-stage-tests.md` before editing integration tests.

## E2E

- Use the project's full-stack runtime for orchestration (for example Tilt or a deployed stack).
- Tests run on the host against port-forwards or exposed endpoints.
- Prefer the repository runner around the runtime command (for example `tilt ci` or `tilt up`).
- Do not use Docker Compose as the default E2E orchestration path.
- Read `e2e-tests.md` and `fluent-stage-tests.md` before editing E2E tests. Read the runtime's own skill when you change stack orchestration.

## Browser E2E

- Treat browser tests as E2E tests.
- Use the same full-stack runtime as other E2E tests.
- Use browser automation only for behavior that HTTP-only tests cannot verify.
- Prefer stable behavior selectors such as `data-testid`.
- Setup and patterns: [../../go-browser-tests/SKILL.md](../../go-browser-tests/SKILL.md).

## Command selection

- Prefer existing repository commands over raw tool invocations.
- If no command exists, follow the local Makefile, justfile, or CI pattern before inventing a new one.
- Record exact failures and classify them as code, environment, credentials, or setup.
