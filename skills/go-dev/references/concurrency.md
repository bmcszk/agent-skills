# Go concurrency

Derived from samber/cc-skills-golang (MIT): golang-concurrency/SKILL.md, golang-concurrency/references/{channels-and-select,sync-primitives,pipelines}.md.

Use this when writing or reviewing goroutines, channels, `select`, sync primitives, worker pools, or fan-out. Start with the checklist: a goroutine is a liability until it has an owner and an exit.

Version gate: never use a stdlib API newer than the `go` directive in `go.mod`. Minimum versions are marked with the API.

## Core principles

1. Every goroutine must have a clear exit: a context, a done channel, or a `WaitGroup`. Otherwise it leaks and accumulates until the process dies.
2. Share memory by communicating. A channel transfers ownership explicitly; a mutex protects shared state but leaves ownership implicit.
3. Send copies, not pointers. A pointer over a channel is invisible shared memory.
4. Only the sender closes a channel. A receiver that closes panics the sender's next write.
5. Specify channel direction (`chan<-`, `<-chan`). The compiler then rejects misuse.
6. Default to unbuffered. A buffer hides backpressure unless you measured the need.
7. Always include `ctx.Done()` in a `select`, or the goroutine outlives its caller.
8. Do not call `time.After` in a hot loop. Each call allocates a timer.
9. Track leaks in tests with `go.uber.org/goleak`.

## Which primitive

| Scenario | Use | Why |
|---|---|---|
| Passing data between goroutines | Channel | Ownership transfer is explicit |
| Coordinating lifecycle | Channel plus context | Clean shutdown in `select` |
| Protecting struct fields | `sync.Mutex` / `sync.RWMutex` | Simple critical sections |
| Counters and flags | `sync/atomic` | Lock-free, lower overhead |
| Read-heavy map | `sync.Map` | Optimized for write-once/read-many. Concurrent map read and write crashes the process |
| One-time init, deduplicated work | `sync.Once`, `singleflight` | Execute once |

| Need | Use |
|---|---|
| Wait, errors ignored | `sync.WaitGroup` |
| Wait and collect the first error | `errgroup.Group` |
| Wait, cancel siblings on first error | `errgroup.WithContext` |
| Wait and bound concurrency | `errgroup.SetLimit(n)` |

| Primitive | Notes |
|---|---|
| `sync.Mutex` | Shortest possible critical section; never hold across I/O, network, or a channel operation |
| `sync.RWMutex` | Reads heavily outnumbering writes. Never upgrade `RLock` to `Lock`: release first, then acquire |
| `sync/atomic` | Typed atomics (`atomic.Int64`, `atomic.Bool`, `atomic.Pointer[T]`) since Go 1.19 |
| `sync.Map` | Not for iteration, length, or heavy overlapping writes; use a map plus `RWMutex` there |
| `sync.Pool` | Temp objects in hot paths; `Reset()` before `Put()`, expect unzeroed values from `Get()` |
| `sync.Once` | `OnceFunc`, `OnceValue`, `OnceValues` since Go 1.21 |
| `sync.WaitGroup` | `wg.Go` since Go 1.25 for fire-and-wait work that cannot fail |
| `x/sync/singleflight` | Deduplicate concurrent identical calls (cache stampede) |
| `x/sync/errgroup` | Goroutine group with errors and `SetLimit` |

## Goroutine lifecycle

Never start a goroutine without knowing how it stops. A goroutine needs a stop signal, a way to wait for it, and a decision about who closes its channels.

Recover at goroutine boundaries in production code: a panic inside a goroutine crashes the whole process, and no caller can recover it. This is crash containment, not error handling. `core-go-rules.md` still forbids `panic` for a normal error, and `error-handling.md` owns panic design.

## Channels

- Put direction in signatures so misuse fails at compile time.
- The producer closes its output channel. A receiver never closes.
- Buffer sizes:

| Size | When |
|---|---|
| 0 | Default. Synchronizes sender and receiver, which is the handoff guarantee |
| 1 | Signal channels, or a sender that must not block on one pending item |
| N > 1 | Only with measurement. Record why N, and what happens when the buffer fills |

- `select` multiplexes channel operations. Include `ctx.Done()` in every blocking `select`, and wrap sends too.
- A non-blocking send or receive uses `select` with `default`. It is a poll, so the caller must handle "not ready".
- In a long-running loop, create one `time.NewTimer` and `Reset` it. Since Go 1.23 an unused timer is collected without `Stop`, and a receive from `timer.C` after `Stop` blocks instead of returning a stale value, so the old drain dance is dead code.

## Mutexes and shared state

- Hold the lock for the shortest time possible. Never hold it across I/O, a network call, or a channel operation.
- Embed the mutex as an unexported field directly above the fields it protects:

```go
type counter struct {
	mu sync.Mutex
	n  int
}
```

- A map shared by goroutines needs a mutex. Concurrent writes crash the runtime, and no test catches it without `-race`.

## WaitGroup, errgroup, singleflight

- `wg.Go(func(){ ... })` (Go 1.25) adds the goroutine and removes it on return. The function must not panic, and a `WaitGroup` propagates no errors and cancels no siblings. Below 1.25, call `Add` before `go`, never inside the goroutine.
- Use `errgroup.WithContext` when goroutines can fail, and `SetLimit` when fan-out is unbounded or input-sized. This replaces a hand-rolled worker pool for most work.
- `singleflight` only when the repo already depends on `golang.org/x/sync` or the deduplication need is real now.

## Pipelines, fan-out, and workers

- Each stage accepts and respects context, and selects on `ctx.Done()`.
- The first stage closes its output; each later stage closes its own output.
- Never spawn unbounded goroutines inside a stage.
- Fan-out means several goroutines read one channel; fan-in means several channels merge into one. Both halves need the close rule above.
- A hand-rolled worker pool is justified only for per-worker state (connections, buffers), custom priority or backpressure, or graceful draining of in-flight work.
- A bare semaphore is for fine-grained limits where errors do not need propagation. When errors matter, `errgroup.SetLimit` wins.
- For in-process transformation with no I/O, iterators (Go 1.23 range-over-func) avoid goroutine and channel overhead. Use a goroutine pipeline when stages do I/O, need real parallelism, or have different throughput.

## Leak detection

- `goleak.VerifyTestMain(m)` in `TestMain` for packages with goroutines. `goleak.VerifyNone(t)` for one test. This complements the go-tests law that integration stages poll for eventual consistency: polling proves the behaviour, goleak proves nothing was left behind.
- `/debug/pprof/goroutine?debug=2` for a stack dump, and `runtime.NumGoroutine()` for a cheap count.
- `/debug/pprof/goroutineleak` (Go 1.27, no build flag) finds goroutines blocked forever on a sync primitive.
- `go test -race ./...` on concurrent code, in CI too.

## Checklist before spawning

- How will it exit?
- Can I signal it to stop?
- Can I wait for it?
- Who owns and closes its channels?
- Would synchronous code be enough? Do not add concurrency without measured need.

## Common mistakes

| Mistake | Fix |
|---|---|
| Fire-and-forget goroutine | Give it a stop mechanism |
| Closing from the receiver | Only the sender closes |
| `time.After` in a hot loop | One `time.NewTimer` plus `Reset` |
| Missing `ctx.Done()` in `select` | Always select on context |
| Unbounded spawning | `errgroup.SetLimit` or a semaphore |
| Sharing a pointer over a channel | Send copies or immutable values |
| `wg.Add` inside the goroutine | `Add` before `go` |
| Mutex held across I/O | Shrink the critical section |
| No `-race` in CI | Run `go test -race ./...` |
