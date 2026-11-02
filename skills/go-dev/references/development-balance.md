# Development decision balance

Use this when making, reviewing, or planning development changes.

Every recommendation balances three lenses:

| Lens | What it means |
|------|----------------|
| Repo consistency | Match the closest existing service, repository convention, build and test workflow, naming style, and operational pattern. |
| Good practices | Correct error handling, testability, maintainability, security, observability, and language or framework idioms. |
| Minimalism and readability | Smallest clear change, no speculative abstractions, easy to scan, focused review diffs. YAGNI and ponytail apply here. |

## Priority when lenses conflict

The order is in [../SKILL.md](../SKILL.md#decision-order). Safety means: never simplify away validation at trust boundaries, error handling that prevents data loss, security, or anything the user explicitly requested.

## Decision rules

- Prefer a local repo pattern over a generic best practice unless the local pattern is clearly broken or unsafe.
- Prefer a simple readable implementation over a more abstract one unless the abstraction removes real duplication or risk now, not someday.
- Prefer explicit verification over confidence from style or convention.
- Keep critique and implementation grounded in the current repository instead of optimizing for theoretical purity.
- If the lenses still conflict after the priority order, state the tradeoff briefly and choose the option with the least operational and review risk.

The review filter is in [core-go-rules.md](core-go-rules.md#review-filter).

## Go examples

| Situation | Prefer | Avoid |
|-----------|--------|-------|
| New HTTP handler test | Integration test with the fluent `given` / `when` / `then` stage | Mocking the DB in a unit test because it is less code |
| Pure validation function | Small unit test with `// given` / `// when` / `// then` | Integration test through HTTP for logic with no dependencies |
| Interface for one implementation | Concrete type at the producer; interface at the consumer when a consumer needs one | New `interfaces.go` or speculative abstraction |
| Goroutine fan-out with errors | `errgroup` with `SetLimit` | Bare `sync.WaitGroup` because it is shorter |
| New helper package | Inline in the owning package until reuse is real | `utils` or `types` package for one caller |
| Error from external call | Wrap with `%w` and operation context | Raw return or string concat because wrapping feels verbose |
| Test for behaviour needing DB | Integration test with Docker Compose | Mocks |

## Ponytail markers

When you deliberately choose simplicity over a heavier pattern, mark it so review reads intent, not omission:

```go
// ponytail: linear scan; index map if this grows past ~100 items
```

Use it only when the simpler choice has a known ceiling and upgrade path. In Go code this marker replaces the `shortcut:` marker from the ponytail skill.
