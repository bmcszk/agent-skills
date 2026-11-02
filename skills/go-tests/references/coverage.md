# Code coverage

Derived from samber/cc-skills-golang (MIT): golang-testing/references/coverage.md.

Use this when reading a coverage report or deciding what to test next. Coverage is a gap finder, not a target: it measures which lines ran, not whether their behaviour was asserted. Adding a unit test only to raise the number is forbidden in [unit-tests.md](unit-tests.md).

## Commands

```bash
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out          # uncovered lines in red
go tool cover -func=coverage.out          # per function
go tool cover -func=coverage.out | grep total
go test -covermode=count -coverprofile=coverage.out ./...
go test -race -covermode=atomic -coverprofile=coverage.out ./...
go test -coverpkg=./... ./...             # attribute package A's coverage to tests in B
go test -cover ./internal/store
```

## Modes

| Mode | Records | Use when |
|---|---|---|
| `set` | Whether a statement ran (default) | Normal runs |
| `count` | Executions per statement | Finding never-taken branches in hot paths |
| `atomic` | Count, race-safe | Any run combined with `-race` or `t.Parallel()` |

## Pitfalls

- Per package by default. Without `-coverpkg`, a test in `api` that exercises `store` reports nothing for `store`, so a well-tested package looks untested.
- Integration and E2E tests are invisible unless their own paths are included. This repo splits levels by directory (`test/integration/`, `test/e2e/`), so cover those paths explicitly in the same command, for example `go test -coverpkg=./... ./... ./test/integration/...`. There is no build tag to pass.
- Generated code inflates the number. Exclude it before setting any threshold, or the metric measures the generator.
- A covered line is not an asserted line. A test that calls a function and ignores the result reports full coverage and verifies nothing.
