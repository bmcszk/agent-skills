# Benchmarks

Derived from samber/cc-skills-golang (MIT): golang-testing/references/benchmarks.md.

Use this when writing or reviewing a benchmark that sits next to the tests of the package it measures. Measurement methodology (profiling, `benchstat` comparison, CI regression detection) belongs to [../../go-dev/references/performance.md](../../go-dev/references/performance.md).

## Shape

One benchmark function per candidate, with a sub-benchmark per variant:

```go
func BenchmarkStringConcatenation(b *testing.B) {
    b.Run("plus-operator", func(b *testing.B) {
        for b.Loop() {
            _ = "a" + "b" + "c"
        }
    })

    b.Run("strings.Builder", func(b *testing.B) {
        for b.Loop() {
            var builder strings.Builder
            builder.WriteString("a")
            builder.WriteString("b")
            builder.WriteString("c")
            _ = builder.String()
        }
    })
}
```

Sub-benchmark names are what comparison tooling diffs. One benchmark mixing two variants reports one number and hides the difference.

## Vary the input size

```go
func BenchmarkFibonacci(b *testing.B) {
    for _, size := range []int{10, 20, 30} {
        b.Run(fmt.Sprintf("n=%d", size), func(b *testing.B) {
            b.ReportAllocs()
            for b.Loop() {
                Fibonacci(size)
            }
        })
    }
}
```

Size-parameterized sub-benchmarks expose complexity growth. A jump that outpaces the size increase points at a superlinear algorithm, which a single-size benchmark never shows.

## `b.Loop()` instead of `b.N`

For Go 1.24 and newer, write new benchmarks with `b.Loop()`. It keeps setup out of the timed region and stops the compiler from optimizing the loop body away, the two failure modes that make a `b.N` benchmark look impossibly fast.

Version gate: never use a stdlib API newer than the `go` directive in `go.mod`. Keep a `b.N` loop only when the module targets Go below 1.24, or when intentionally preserving existing benchmark code.

## Reporting

- `b.ReportAllocs()` when allocations are part of the claim.
- `b.ResetTimer()` after heavy setup that a `b.Loop()` benchmark already excludes.
- Run the comparison serially. Concurrent benchmark runs on a shared CPU produce contaminated numbers.
