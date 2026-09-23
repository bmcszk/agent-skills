---
name: go-dev
description: 'Go development best practices, coding patterns, and code standards for production-ready Go applications. Use when writing new Go code, reviewing Go code, refactoring, implementing concurrency, or designing interfaces and generics. Covers inline interfaces, error handling, errgroup concurrency, generics, testing excellence. Keywords: go development, golang best practices, go code review, go concurrency, go generics, go interfaces.'
license: MIT
metadata:
  audience: developers
  workflow: development
  category: backend
  technologies: go, clean-code, concurrency, generics
---

## What I do

I enforce Go development best practices including:
- Inline Interface Definition
- Error handling standards
- Concurrency patterns with errgroup
- Interface design
- Generics usage
- Performance optimization
- Testing excellence

## When to use me

Use this skill when:
- Writing new Go code
- Reviewing Go code
- Refactoring existing code
- Implementing concurrent operations
- Designing interfaces and generics

## Related Skills

- `go-setup` - Project initialization and library selection
- `go-fluent-testing` - Unit/integration/E2E testing (fluent Given/When/Then)

---


## References

Deep-dive topics are split into focused reference files:

- [Interfaces](references/interfaces.md) — Inline interface definition, small focused interfaces, functional options
- [Error Handling](references/errors.md) — Golden rules, wrapping, sentinel errors, multi-error handling
- [Concurrency](references/concurrency.md) — errgroup, worker pools, channel patterns
- [Generics](references/generics.md) — Type parameters, constraints, data structures, decision framework
- [Testing](references/testing.md) — Table-driven tests, mocks, benchmarks, fuzzing
- [Performance & Footguns](references/performance.md) — Pre-allocation, sync primitives, common pitfalls

# Quick Reference Tables

## Error Handling

| ✅ Do This | ❌ Never This |
|-----------|--------------|
| `errors.Is(err, ErrX)` | `err == ErrX` |
| `errors.As(err, &target)` | `err.(*Type)` |
| `fmt.Errorf("...: %w", err)` | `fmt.Errorf("...: %v", err)` |
| `errors.Join(errs...)` | Manual error collection |

## Concurrency

| ✅ Do This | ❌ Never This |
|-----------|--------------|
| `errgroup.WithContext(ctx)` | Bare `sync.WaitGroup` |
| `g.SetLimit(n)` | Unbounded goroutines |
| Loop variable capture | Range variable in goroutine |
| Context for cancellation | Global done channels |

## Testing

| Command | Description |
|---------|-------------|
| `go test -v` | Verbose output |
| `go test -race` | Run race detector |
| `go test -cover` | Show coverage |
| `go test -bench .` | Run benchmarks |
| `go test -fuzz Fuzz` | Run fuzzing |
