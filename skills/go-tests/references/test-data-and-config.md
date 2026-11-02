# Test data, doubles, async checks, and config

Use this when a test needs request fixtures, a fake upstream server, eventual-consistency checks, or environment configuration.

## Async checks

For eventual consistency, `then` methods add checks to `stage.checks`. One final `then` method runs them all with polling. Each check returns an `error`, so the timeout reports the last failure of every check.

```go
type checks struct {
    interval, timeout time.Duration
    fns               []func() error
}

func (s *stage) orderHasStatus(want string) *stage {
    s.checks.fns = append(s.checks.fns, func() error {
        got, err := s.fetchOrderStatus()
        if err != nil {
            return fmt.Errorf("fetch order status: %w", err)
        }
        if got != want {
            return fmt.Errorf("status: want %q, got %q", want, got)
        }
        return nil
    })
    return s
}

func (s *stage) allChecksPass() *stage {
    s.require.EventuallyWithT(func(c *assert.CollectT) {
        for _, fn := range s.checks.fns {
            assert.NoError(c, fn())
        }
    }, s.checks.timeout, s.checks.interval)
    return s
}
```

Use longer `timeout` and `interval` on CI, because shared runners are slower. Choose them in the checks constructor:

```go
func newChecks() *checks {
    if os.Getenv("CI") == "true" {
        return &checks{interval: 2 * time.Second, timeout: 60 * time.Second}
    }
    return &checks{interval: 500 * time.Millisecond, timeout: 20 * time.Second}
}
```

Poll. Do not `time.Sleep` to wait for an async result.

## Test data

- Keep long request bodies in committed fixtures (`test/data/`), rendered from a template with the dynamic values. Do not build multi-line bodies with `fmt.Sprintf` in a scenario. Short single-line bodies may stay inline.
- Keep one `test/data/` tree. Dissolve stray directories such as `test/fixtures/`, and grep `*.go` and `*.md` for stale paths in the same change.
- A `given` method renders the template and stores the result on `stage`:

```go
func (s *stage) anOrderWithItems(count int) *stage {
    tmpl, err := template.ParseFiles(filepath.Join("test", "data", "order.json.tmpl"))
    s.require.NoError(err)

    var buf bytes.Buffer
    s.require.NoError(tmpl.Execute(&buf, map[string]any{"Items": count}))
    s.requestBody = buf.String()
    return s
}
```

## Fake upstream servers

- A fake upstream server stays a short echo handler that records requests on `stage`. Assert the recorded method, path, headers, and body in `then` methods, not with `t.Errorf` inside the handler.
- The same handler shape in three or more tests becomes one `given` method (`aJSONEchoServer()`, `anUpstreamReturning(status)`).
- When a `then` needs a list of rules, pass one inline struct slice to one `then` method. Do not add a builder function per fixture.

```go
then.
    serverReceivedMethodAndPath(0, http.MethodPost, "/orders").and().
    serverReceivedHeader(0, "Content-Type", "application/json")
```

- Call `t.Helper()` in helper methods, not in `Test*` functions.

## Cleanup

- Register cleanup with `t.Cleanup` in the `given` method that creates the resource.
- A cleanup step logs a failure and continues. A nil client or missing table must not hide the real test result:

```go
t.Cleanup(func() {
    if _, err := s.db.Exec("DELETE FROM orders WHERE id = $1", s.orderID); err != nil {
        s.Logf("cleanup orders: %v", err)
    }
})
```

## Config

- Read endpoints and credentials for the stack from environment variables with local defaults (`TEST_SERVICE_ADDRESS`, `TEST_DB_URL`). Do not hard-code hosts in scenarios.
- `newStage(t)` reads the environment once and stores the values on `stage`.
- Commit no secrets. Tests use throwaway local credentials only.

## Layout

```text
test/
  data/                 committed fixtures and templates
  integration/
    orders_test.go      scenarios
    orders_stage_test.go
    stage_test.go       base stage, newStage, checks
  e2e/
    orders_test.go
    orders_stage_test.go
    stage_test.go
```
