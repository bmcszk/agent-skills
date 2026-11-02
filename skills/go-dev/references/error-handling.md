# Go error handling

Derived from samber/cc-skills-golang (MIT): golang-error-handling/SKILL.md, golang-error-handling/references/{error-creation,error-wrapping,error-handling}.md.

Use this when creating an error, deciding how to wrap or inspect one, choosing where it gets logged, or reviewing panic and recover. [core-go-rules.md](core-go-rules.md) holds the safety baseline (`%w`, `errors.Is`, `errors.As`, no swallowed errors). This ref explains the choices behind it.

Version gate: never use a stdlib API newer than the `go` directive in `go.mod`. Minimum versions are marked with the API.

## Error strings

- Lowercase, no trailing punctuation, no newline.
- Describe what happened, not what the caller should do about it.
- Do not repeat context the wrapping layer will add.

```
failed to connect to database: dial tcp 127.0.0.1:5432: connection refused
```

Each layer contributes one prefix, so the chain reads as a sequence of operations.

## Creating an error

| Situation | Strategy |
|---|---|
| Caller matches a specific condition | Sentinel: `var ErrNotFound = errors.New("not found")` |
| Caller extracts structured data | Custom type with fields |
| Informational, never matched | `fmt.Errorf` or `errors.New` with operation context |
| Needs stack traces or request attributes | A custom type carrying them, plus structured log attributes |

- A sentinel is a package-level value, allocated once. Comparing by identity is the point.
- A custom type that wraps another error implements `Unwrap() error`, so `errors.Is` and `errors.As` can walk through it.
- Do not reach for a third-party error library. `fmt.Errorf("%w")`, a custom type, and `slog` cover stack traces, context, and codes.

## Low-cardinality messages

Log aggregators group events by the message template or the error fingerprint. A stable template with variable data glued in creates one group per unique value, which breaks dashboards and alerting.

- Keep the message template fixed: `fmt.Errorf("fetching user: %w", err)` is fine, because the prefix never changes.
- Attach IDs, paths, counts, and durations as structured attributes, not as message text.
- Variable text in a returned error is acceptable for a CLI. Production logging keeps the grouping key stable.
- Error values may carry operational context. Keep what gets grouped low-cardinality.

## Wrapping and inspection

- `%w` inside the module, so the chain survives.
- `%v` at a public API or system boundary, so callers do not depend on internal types.
- `errors.Is` for a sentinel. Never compare with `==`, except against `nil`.
- `errors.As` to extract a typed error. On Go 1.26 and newer, `errors.AsType[*MyError](err)` returns `(value, ok)` and avoids the declared target variable.
- `errors.Join` (Go 1.20) combines independent errors, and `errors.Is` sees through the join. Use it to report every failed validation field at once, or every failure of parallel work.

## The single handling rule

An error is handled exactly once: logged or returned, never both. Doing both produces duplicate log lines and makes the real origin hard to find.

- Adding context and returning is not handling. That is wrapping.
- Logging belongs at the boundary that owns the decision: the handler, the worker loop, the `main` function.
- Swallowing with `_ =` is a bug, not a style choice. If the error truly does not matter, log it at debug level with the reason.
- At an HTTP handler boundary, log the technical error and return a translated user-facing message. Never expose driver or internal errors to a client. The response side (HTML, HTMX, status) belongs to [go-htmx-frontend](../../go-htmx-frontend/SKILL.md); this ref covers the log-and-return discipline.

## Panic and recover

- `panic` is for a state the program cannot continue from: a broken invariant, a programmer error, an impossible branch. `core-go-rules.md` forbids it for normal error handling, and a value that any caller can send is normal error handling.
- Never panic for a timeout, a missing file, a bad request, or an unexpected enum from input. Return an error.
- `recover` in a deferred function at a process boundary: goroutine entry points, HTTP middleware, worker loops. One panicking goroutine otherwise takes down the process.
- A recovery converts the panic into an error or a 500 response, logs it with the stack, and keeps the process alive.
- Do not use panic and recover for control flow. Unwinding runs every deferred call and allocates a stack trace; the cost dwarfs a returned error.

## Structured logging

- Use `log/slog`. Not `fmt.Println`, not `log.Printf`.
- Use typed attributes: `slog.String`, `slog.Int`, `slog.Duration`. `slog.Any` boxes and allocates.
- One event, one log call, one level. A failed request logs once, at the level the operator needs.
- Keep PII out of error messages and attributes: no tokens, no full request bodies, no email addresses in the message template.
- Attach the error itself with `slog.Any("error", err)`, and put the grouping key in the message, not the attributes.
- Vendor wiring for trace and APM exporters is deployment configuration, not this skill's business.

## Review checklist

- Every returned error checked, none dropped with `_`.
- Every wrap has a `%w` and an operation prefix.
- `errors.Is` / `errors.As` instead of `==` or a bare type assertion.
- No log-and-return pair on the same error.
- No `panic` on a reachable input.
- A goroutine boundary has a recover.
- Logged messages stay low-cardinality and free of PII.
