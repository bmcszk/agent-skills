# Go performance

Derived from samber/cc-skills-golang (MIT): golang-performance/SKILL.md, golang-performance/references/{memory,cpu,io-networking,caching,runtime,observability}.md.

Use this when profiling or a benchmark has identified a bottleneck and you need the pattern that fixes it, or when reviewing code for structural performance problems.

Version gate: never use a stdlib API newer than the `go` directive in `go.mod`. Minimum versions are marked with the API.

## Method

1. Profile before optimizing. Intuition about the hot spot is wrong about 80% of the time.
2. Allocation reduction has the best return. Go's GC is fast but not free, and fewer allocations per request usually beats micro-optimizing CPU.
3. Rule out external bottlenecks first. If most of the latency is a slow query or a slow API call, allocation work changes nothing.
4. Change one thing, then re-measure. Document the optimization with its numbers.

One short comment is allowed for a non-obvious optimization, under the [coding-rules](../../coding-rules/SKILL.md) comment law: state why it is faster and by how much, so the next reader does not revert it.

## Rule out external bottlenecks

| Diagnose | Reading |
|---|---|
| `fgprof` | On-CPU and off-CPU time. Off-CPU dominating means I/O wait |
| `go tool pprof` goroutine profile | Many goroutines blocked in `net.(*conn).Read` or `database/sql` means external wait |
| Distributed tracing | Span breakdown names the slow upstream |

When the bottleneck is external, work that component: query tuning, caching, connection pools. See [database.md](database.md) and the caching section below.

## Cycle

1. Define the metric: latency, throughput, memory, or CPU. Without a target, the change is random.
2. Write an atomic benchmark for one function, so results do not contaminate each other.
3. Baseline: `go test -bench=BenchmarkX -benchmem -count=6 ./pkg/... | tee /tmp/report-1.txt`.
4. Read the Diagnose lines in the matching section below to pick the tool.
5. Apply one change.
6. Compare: `benchstat /tmp/report-1.txt /tmp/report-2.txt` (`go install golang.org/x/perf/cmd/benchstat@latest`).
7. Record the benchstat output in the commit body, so the improvement is auditable.
8. Repeat with the next bottleneck.

Run benchmark variants serially. Concurrent runs on a shared CPU produce contaminated numbers even when the implementations were built in parallel.

## Decision tree

| Signal | Cause | Read |
|---|---|---|
| `alloc_objects` high in the heap profile | Too many allocations | Memory |
| One function dominates the CPU profile | CPU-bound hot loop | CPU |
| High GC percentage, OOM kills, container limits | GC and memory limits | Runtime |
| Goroutines blocked on I/O | Network or disk latency | I/O |
| The same expensive work repeated | Missing cache or deduplication | Caching |
| O(n²) where O(n) exists | Wrong algorithm | Complexity |
| Mutex or block profile hot | Lock contention | [concurrency.md](concurrency.md) |
| DB time dominates the trace | Slow queries | [database.md](database.md) |

## Memory

Diagnose: `go tool pprof -alloc_objects` (rank by allocation count), `go build -gcflags="-m -m"` (why a value escapes), `go test -bench -benchmem` (allocs/op and B/op).

Allocation patterns:

- Reuse a slice with `s[:0]`, which keeps the backing array and skips a new allocation.
- When output size equals input size, `make([]T, len(in))` with direct assignment beats `make([]T, 0, len(in))` plus `append`. Keep `append` when filtering or when an early error may discard partial results.
- Capture the value in `for k, v := range m`, instead of `m[k]` inside the loop.
- Give `make(map[K]V, n)` a size hint when the size is known, to skip rehashing. No speculative hints: [style.md](style.md).
- A preallocated sentinel error beats `fmt.Errorf` on a hot path.
- Passing a concrete type through `any` boxes and allocates. Use a typed parameter or generics.

Backing-array retention:

- A small reslice of a large slice keeps the whole array alive. Copy what you keep.
- A substring shares the source string's array. Copy short-lived substrings out of large ones.
- A map releases no bucket memory after deletes. Replace it, or bound its size.

Strings and bytes: convert once and reuse; prefer `bytes.Contains` / `HasPrefix` / `Split` over a string round-trip.

`sync.Pool`:

- For frequently allocated short-lived objects on a hot path (buffers, encoders, temp structs).
- `Reset()` before `Put()`, so no large object graph survives the cycle.
- Return copies, never the pooled buffer itself.
- Do not pool objects above about 32KB, or rarely used objects. The overhead beats the gain.

Memory layout:

- Reorder struct fields largest first: `int64`, `float64`, `string`, slice, and pointer are 8-byte aligned; `int32` and `float32` 4; `int16` 2; `bool` and `byte` 1.
- `fieldalignment ./...` reports wasted padding. Confirm savings with `unsafe.Sizeof`, and record the number in the comment.
- A zero-size last field (`struct{}`) costs a word of padding. Do not add one for layout reasons.
- Pointer receivers for structs above about 128 bytes. If one method needs a pointer receiver, make them all pointers.
- `map[K]*V` avoids copy-modify-reassign for large, frequently updated structs, at the cost of one heap object and GC pressure.

## CPU

Diagnose: `go tool pprof` CPU profile for the dominant function, `go build -gcflags="-m"` for `cannot inline` reasons.

- Small functions inline. Loops, many statements, or calls to non-inlinable functions block it. Keep logging and metrics out of the hot function, or guard them.
- Value receivers let the compiler inline a fluent chain; a pointer receiver adds indirection.
- Cache locality: traverse in the layout order (row-major for 2D), allocate a 2D matrix as one contiguous block, and prefer a struct of arrays when a loop touches one field of many. Expected 10 to 50 times difference on large data.
- Index-based contiguous nodes beat pointer-chasing for traversal-heavy structures.
- False sharing: goroutines writing different variables on the same 64-byte cache line invalidate each other. Pad only after the profile shows contention. A symptom is adding goroutines making the loop slower.
- Instruction-level parallelism: a single accumulator in a tight arithmetic loop chains dependencies. Two to four accumulators help when the loop is truly CPU-bound.
- SIMD: let the compiler auto-vectorize simple numeric loops first. `simd/archsimd` (Go 1.26, `GOEXPERIMENT=simd`) and the portable `simd` package (Go 1.27) are experimental, may change, and must not appear in a public API. `math/bits` maps to hardware instructions. Hand-written assembly and `//go:build` variants are a build-time feature gate for a numeric inner loop above 20% of CPU, never a test gate. Prefer runtime CPU feature detection when one binary must run on mixed hardware.
- A very tight loop with no calls can starve other goroutines despite async preemption (Go 1.14+). If trace shows starvation and the burst exceeds tens of milliseconds, a non-inlined call yields. `//go:noinline` costs 10 to 30 cycles per call, so use it only when the profile proves starvation.
- `reflect` in a hot path costs 10 to 100 times; `reflect.DeepEqual` 50 to 200 times. Use `slices.Equal`, `maps.Equal`, `bytes.Equal`, or a type switch.
- `time.Since(start)` uses the monotonic clock, so wall-clock adjustments cannot skew a measurement.

## Runtime

Diagnose: `GODEBUG=gctrace=1` (one line per cycle: cycle number, time since start, GC CPU percent, heap before → peak → after, goal, P count), `runtime.ReadMemStats`, `debug.ReadGCStats` for pause percentiles, `runtime/metrics`, `go tool trace`.

- `GOGC` (default 100) triggers a collection when the heap doubles. Higher means fewer collections and more memory.
- `GOMEMLIMIT` (Go 1.19) is a soft limit; the pacer collects more eagerly as the heap approaches it. Set it inside a container to survive an OOM kill.
- Reducing allocations beats tuning `GOGC`, because it removes the cause instead of managing the symptom.
- `GOMAXPROCS`: Go 1.25 and newer derive it from the cgroup quota on cgroup v2. Below 1.25, or on cgroup v1, validate the value at startup and consider `go.uber.org/automaxprocs` only if the repo already needs it.
- PGO (Go 1.21): a `default.pgo` file in the main package directory, taken from 30+ seconds of representative load, gives 2 to 7% through better inlining and devirtualization. Rebuild after significant code changes.
- Logging in a hot path allocates even when the level discards the message. Use `slog.LogAttrs` with typed attributes.
- `panic`/`recover` as control flow costs 10 to 100 times a returned error, through stack unwinding and deferred calls.

## I/O and networking

Diagnose: goroutine and block profiles for goroutines in `dialConn` / `readLoop`, `fgprof` for off-CPU time, `-inuse_space` for MB-sized single allocations.

- The default `http.Transport` keeps only 2 idle connections per host (`MaxIdleConnsPerHost`). Raise it to the concurrency level, and set `MaxIdleConns`.
- Zero-value `http.Client` and `http.Server` have no timeouts. A slow peer then holds descriptors and memory forever. Set them.
- A response body must be fully read and closed to return the connection to the pool. Drain it even when the body is unused.
- `io.ReadAll` buffers the whole stream. Stream with `io.Copy` for large payloads; it is fine below about 1MB.
- `json.NewDecoder` streams; `json.Unmarshal` buffers. For hot paths, consider a hand-written `MarshalJSON`, a code generator, or `encoding/json/v2`, whose behaviour differs from v1: read [modern-go.md](modern-go.md) before switching.
- A cgo call costs about 50 to 100ns, pins the goroutine to a thread, and cannot be preempted. Do not put one in a hot loop for a small win.
- `bufio.Reader` / `bufio.Writer` collapse many small syscalls into a few.
- Batch work: one insert of 1,000 rows beats 1,000 round trips; one API call with N items beats N calls; drain a channel in batches when per-item overhead dominates.
- Run pipeline stages concurrently only when each saturates a different resource, ordering does not matter, and buffer memory is acceptable. Otherwise a sequential loop with batching is simpler and often faster.

## Caching

Diagnose: `regexp.Compile` / `template.Parse` in the CPU profile, goroutines blocked on the same fetch (cache stampede), member scans in a hot loop.

- Compile a regular expression once at package level. `regexp.MustCompile` is fine for a constant pattern and panics on an invalid one at startup; use `regexp.Compile` for a user-supplied pattern.
- Parse templates once at startup, not per request.
- Replace a pure computation on a small input space with a precomputed table that fits in cache.
- `singleflight` collapses concurrent identical misses into one fetch. See [concurrency.md](concurrency.md).
- A cache needs a bound and an eviction policy. The repo's existing cache dependency decides which; do not add one for a single call site. See [database.md](database.md) for pool and batch interactions.

Algorithmic complexity comes before constant factors:

| Pattern | Cost | Fix |
|---|---|---|
| `slices.Contains` inside a loop | O(n·m) | Build a `map[T]struct{}` first |
| Nested matching loops | O(n²) | Index by map, or sort plus binary search |
| `append` without preallocation | Amortized copying | `make([]T, 0, n)` |
| `+=` string concatenation in a loop | O(n²) copies | `strings.Builder` |
| Linear min/max/dedup per query | O(n) per query | Sort once, query many |

Work avoidance:

- A membership test against the same collection becomes one map lookup.
- Return as soon as the answer is known.
- A direct loop beats a chain of iterator closures: fewer allocations and better inlining.
- A wrapper that only calls another function through a closure blocks inlining. Write the loop.

## Production signals

When the service already exports Prometheus metrics, these are the useful ones and what they mean:

| Metric | Reading |
|---|---|
| `rate(go_gc_duration_seconds_count[5m])` | GC cycles per second; sustained above 2 suggests too many allocations |
| `go_gc_duration_seconds{quantile="1"}` | Worst pause; spikes cause tail latency |
| `go_memstats_alloc_bytes` | Stable under constant load; a steady climb is a leak |
| `rate(go_memstats_alloc_bytes_total[5m])` | Allocation rate; compare before and after a deploy |
| `go_goroutines` | Should track load; growth without traffic is a leak |
| `rate(process_cpu_seconds_total[5m]) / GOMAXPROCS` | Above 0.8 sustained means CPU-saturated |

Continuous profiling (Pyroscope, Parca, a vendor agent) over about 1 to 5% overhead is worth adding only after local profiling stops explaining the regressions. Dashboard and alert assets are deployment configuration, not skill content.

## Common mistakes

| Mistake | Fix |
|---|---|
| Optimizing without a profile | Profile first |
| Default `http.Client` transport | Raise `MaxIdleConnsPerHost` to the concurrency level |
| Logging in a hot loop | `slog.LogAttrs` outside the hot function |
| `panic` as control flow | Return an error |
| `unsafe` for a guess | Only with a benchmark showing more than 10% in a verified hot path |
| No memory limit in a container | `GOMEMLIMIT` to 80-90% of the limit |
| `reflect.DeepEqual` in production | Typed comparison |
