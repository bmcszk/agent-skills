# Unit tests

Use this when adding or changing Go unit tests.

## Scope

Unit tests are only for pure, easily testable functions, ideally public functions or methods, that you can verify with direct inputs, outputs, and returned errors.

Best fits:
- validation
- parsing
- mapping
- formatting
- deterministic calculations
- simple business rules

Avoid unit tests for:
- orchestration
- workflows
- HTTP handlers
- database behavior
- messaging behavior
- time-dependent flows
- dependency-heavy behavior
- anything that would need mocks, stubs, or fakes

If a function needs a mock, stub, or fake to test, it belongs in an integration or E2E test instead.

## Rules

The hard rules (file per source file, blackbox package, no mocks, outcomes and tables, phase markers) are in [SKILL.md](../SKILL.md#hard-rules-unit). In addition:

- Test only exported functions and methods. Do not access unexported fields or private functions.
- Do not add unit tests only to increase coverage.
- Name tests `TestSubject_Scenario_Outcome`, for example `TestValidateEmail_Empty_ReturnsError`.
- Name the other test kinds after the subject too: `BenchmarkSubject` (variants as sub-benchmarks), `ExampleSubject` and `ExampleSubject_variant`, `FuzzSubject`. Only `Test*` functions carry the scenario and outcome suffix, because only they encode one outcome each.
- A benchmark that compares implementations or input sizes is one function with sub-benchmarks, so each variant gets its own name. Shape and `b.Loop()` rules: [benchmarks.md](benchmarks.md). Examples: [examples.md](examples.md).
- Keep state local to the test function. The stage struct is for integration and E2E tests.
- Phase roles match fluent stages: [fluent-stage-tests.md](fluent-stage-tests.md#given--when--then-roles).

## Example

```go
func TestValidateEmail_Valid_ReturnsNil(t *testing.T) {
    // given
    email := "ada@example.com"

    // when
    err := validation.ValidateEmail(email)

    // then
    require.NoError(t, err)
}

func TestValidateEmail_Invalid_ReturnsError(t *testing.T) {
    tests := []struct {
        name    string
        email   string
        message string
    }{
        {name: "empty", email: "", message: "email is required"},
        {name: "no at sign", email: "ada.example.com", message: "email must contain @"},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // given
            email := tt.email

            // when
            err := validation.ValidateEmail(email)

            // then
            require.ErrorContains(t, err, tt.message)
        })
    }
}
```

## Assert scope in subtests

Never build a testify `assert`/`require` instance in the parent test and reuse it inside `t.Run`. `assert.New(t)` captures the exact `*testing.T` it was built from, so a failure inside the subtest is reported against the parent, while the failing subtest still prints `--- PASS`. The output then hides which case broke, with or without `t.Parallel()`.

```go
// wrong: is belongs to the parent t
is := assert.New(t)
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        is.Equal(tt.want, got)
    })
}

// right: each subtest builds its own from its own t
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        is := assert.New(t)
        is.Equal(tt.want, got)
    })
}
```

Verify with a deliberately broken row: if `go test -v -run TestName` shows `--- FAIL: TestName` while every `--- PASS: TestName/subtest` still says PASS, the scope is leaking.

## Fuzzing

A fuzz target states an invariant that must hold for every input, and the engine finds the input that breaks it:

```go
func FuzzReverse(f *testing.F) {
    f.Add("hello")
    f.Add("")

    f.Fuzz(func(t *testing.T, input string) {
        if got := Reverse(Reverse(input)); got != input {
            t.Errorf("Reverse(Reverse(%q)) = %q", input, got)
        }
    })
}
```

- Seed with a few literal values, including the empty one.
- Assert an invariant, not a hard-coded expected value. A fuzz target that repeats a table row adds nothing.
- Run locally with `go test -fuzz=FuzzReverse ./<pkg>`. A failing input is written to `testdata/fuzz/`, so commit it as a regression case.
- A fuzz target follows the same scope law as any unit test: pure code, no mocks, no services.

## Fake time with synctest

`testing/synctest` (Go 1.25) runs goroutines in an isolated bubble where time advances only when every goroutine is blocked. That makes a timeout, a backoff, or a ticker deterministic instead of flaky:

```go
func TestContextTimeout(t *testing.T) {
    synctest.Test(t, func(t *testing.T) {
        const timeout = 5 * time.Second

        ctx, cancel := context.WithTimeout(t.Context(), timeout)
        defer cancel()

        time.Sleep(timeout - time.Nanosecond)
        synctest.Wait()
        require.NoError(t, ctx.Err())

        time.Sleep(time.Nanosecond)
        synctest.Wait()
        require.ErrorIs(t, ctx.Err(), context.DeadlineExceeded)
    })
}
```

- Use `synctest.Test`. The Go 1.24 `synctest.Run` API is experimental and only reachable behind `GOEXPERIMENT=synctest`; do not use it in 1.25+ code.
- `synctest.Wait()` blocks until every goroutine in the bubble is blocked, which is the point where fake time can move.
- Go 1.27 adds `synctest.Sleep(d)`, equivalent to `time.Sleep` plus `synctest.Wait()`, and `httptest.NewTestServer(t, handler)`, an in-memory server that composes with the bubble instead of needing a real socket.
- Version gate: never use a stdlib API newer than the `go` directive in `go.mod`. From Go 1.27, `go test` fails on a newer API through the `stdversion` vet check.
- Fake time does not turn a time-dependent flow into a unit test. The target is a narrow piece whose logic is deterministic under fake time, such as a timeout wrapper or a pacing calculation. Service behaviour with real timers stays in integration or E2E.
