# Examples as documentation

Derived from samber/cc-skills-golang (MIT): golang-testing/references/examples.md.

Use this when a public API deserves a runnable example next to its documentation. `go test` runs each example and compares stdout with the `// Output:` comment, and `pkg.go.dev` renders it beside the documented symbol. An example that drifts from the API fails the build, unlike a code block in a README.

```go
func ExampleCalculatePrice() {
    price := CalculatePrice(100, 10.0)
    fmt.Printf("Price: %.2f\n", price)
    // Output: Price: 900.00
}

func ExampleCalculatePrice_singleItem() {
    price := CalculatePrice(1, 25.50)
    fmt.Printf("Price: %.2f\n", price)
    // Output: Price: 25.50
}
```

## Naming

The suffix decides which symbol the example attaches to, so a typo silently detaches it:

| Function name | Documents |
|---|---|
| `Example()` | The package |
| `ExampleCalculatePrice()` | The function `CalculatePrice` |
| `ExampleStore_Get()` | The method `Get` of `Store` |
| `ExampleStore_Get_cached()` | A named variant of that method |

The suffix after the second underscore starts with a lowercase letter. Otherwise Go reads it as a type or method name and the example is orphaned.

## Output directives

- `// Output:` stdout must match, leading and trailing whitespace trimmed.
- `// Unordered output:` lines may arrive in any order. Use it for map iteration and concurrent producers.
- No output comment: the example compiles but never runs. Useful for code needing a live dependency, but it stops verifying behaviour, so prefer a real assertion.

## Placement

Examples live in `_test.go` files, in the `package foo_test` external test package. An example that compiles only against the exported API proves the public surface is usable, which is the point.
