---
name: go-dev
description: 'Go development best practices, coding patterns, and code standards for production-ready Go applications. Use when writing new Go code, reviewing Go code, refactoring, implementing concurrency, or designing interfaces and generics. Covers inline interfaces, error handling, errgroup concurrency, generics, testing excellence.'
license: MIT
metadata:
  audience: developers
  workflow: development
  category: backend
  technologies: go, clean-code, concurrency, generics
---

## Related Skills

- `go-setup` - Project initialization and library selection
- `go-fluent-testing` - Unit/integration/E2E testing (fluent Given/When/Then)

---


## References

Deep-dive topics are split into focused reference files:

- [Interfaces](references/interfaces.md) - Inline interface definition, small focused interfaces, functional options
- [Error Handling](references/errors.md) - Golden rules, wrapping, sentinel errors, multi-error handling
- [Concurrency](references/concurrency.md) - errgroup, worker pools, channel patterns
- [Generics](references/generics.md) - Type parameters, constraints, data structures, decision framework
- [Testing](references/testing.md) - Table-driven tests, mocks, benchmarks, fuzzing
- [Performance & Footguns](references/performance.md) - Pre-allocation, sync primitives, common pitfalls

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

Race detection is mandatory for concurrent code; coverage and benchmarks
follow the same `go test` flags as any Go project.


## Go embedding
Embedding promotes the embedded struct's members onto the outer type. NEVER re-bind the host inside a method (`p := c.parts` is always wrong): call promoted members on the receiver directly (`c.require`, `c.parsedFile`, `c.aClient()`). A hop is justified ONLY when passing the host as a value. Never build a bidirectional cycle (base embeds sub-structs while sub-structs embed base) - shape promotion one-way. Full rules: references/performance.md §Go embedding.

No `var _ = []any{ Type{} }` compile-assert blocks (or `var _` unused-import silencers) - dead noise; delete and let `unused` name genuinely dead symbols. Full rule: references/performance.md §No lint-appeasement constructs.

## Design acceptance is a gate

Gates (build/vet/lint/tests/parity) verify code correctness: none of them verifies the user accepts the design. A structural/topology change (file layout, struct shapes, DSL patterns) gets user sign-off on ONE probe file before mass application: wave-by-wave shipping of an unconfirmed pattern converts every review into a rewrite. Each stored design rule carries its as-of date; when the user signals the shape is wrong, re-read the rule from scratch instead of re-applying the stored one.

## Fluent-chain shape (Go DSL structs)

A fluent builder chain survives promotion only while every builder returns the SAME concrete type. Prefer ONE struct holding all state with methods on `*parts`-style receivers returning that pointer: mixed-domain chains and `.and()` links then work with zero call-site churn. Before adding wrapper structs, generic self-types, or per-domain return types, prototype the WORST chain in a scratch module (`go mod init` + one test) and check cross-domain links compile: self-typed generics (`parts[S]`) break chains the moment a method from another domain is called, and a `*parts` receiver cannot soundly return a domain-typed `S` (zero value = nil). Go 1.27 generic methods don't fix this. Wrapper-marker structs (stateless `type X struct { base }`) add ctor ceremony without behavior; if state is already flat, they get deleted on the next simplification pass.
