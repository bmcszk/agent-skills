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
