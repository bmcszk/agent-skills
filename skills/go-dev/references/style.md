# Go style

Derived from samber/cc-skills-golang (MIT): golang-code-style/SKILL.md, golang-code-style/references/details.md.

Use this when writing or reviewing Go code and a rule in [core-go-rules.md](core-go-rules.md) does not settle the shape of the code: line breaking, declarations, control flow, function signatures, value versus pointer.

Version gate: never use a stdlib API newer than the `go` directive in `go.mod`. From Go 1.27, `go test` fails on it through the `stdversion` vet check. Minimum versions below are marked with the API.

## Line length and breaking

- No rigid line limit. Break lines past about 120 characters.
- Break at semantic boundaries, not at a column count.
- A call with 4 or more arguments puts one argument per line, closing parenthesis on its own line.
- A signature that needs wrapping usually has too many parameters. Fewer parameters with an options struct beats better wrapping.

## Variable declarations

- `:=` for a non-zero start value, `var` for zero-value initialization. The form states intent: `var` means "this starts at zero".
- Initialize slices and maps explicitly. A nil map panics on write, and a nil slice encodes as `null` while an empty slice encodes as `[]`. If the codec is in question, read [modern-go.md](modern-go.md).
- Preallocate only when the size is known. `make([]T, 0, 1000)` wastes memory when the common case is 10 items.
- Composite literals use field names. Positional fields break when the type adds or reorders a field.

## Control flow

- Handle errors and edge cases first and return. Keep the happy path at minimal indentation.
- Drop the `else` when the `if` body ends in `return`, `break`, or `continue`.
- Assign a default, then override it in a `switch`. An `if / else if / else` assignment chain hides which value is the default.
- An `if` with 3 or more operands gets named booleans, so the condition reads as a rule. Keep an expensive operand inline so short-circuiting still skips it.
- Scope a variable to the `if` when only the check needs it: `if err := validate(in); err != nil`.
- Comparing the same variable more than once reads better as a `switch`.
- A `switch` over an enum returns an error for an unexpected value. `panic` is for states the type system cannot express and no runtime input can reach. A value that a caller can send is normal error handling, and [core-go-rules.md](core-go-rules.md) forbids panicking on it.

## Function design

- One function, one job, short enough to read in one screen.
- At most 4 parameters. Beyond that, an options struct.
- Parameter order: `context.Context` first, then inputs, then output destinations.
- Naked returns only in 1 to 3 line functions where the returned values are obvious. Name them in anything longer.
- Prefer `range` over index loops, and `range n` for counting (Go 1.22).

## Value versus pointer arguments

- Pass `string`, `int`, `bool`, `float64`, and `time.Time` by value. A string is already a pointer and a length.
- Pass a pointer to mutate, when `nil` carries meaning, or for a struct of about 128 bytes or more.
- Do not pass a pointer "to save memory". The copy is negligible and stack allocation is fast. A `*string` costs a dereference and saves nothing.
- Read-only access to a small struct is usually faster by value: no indirection and better cache locality. When in doubt, benchmark.

## Code organization within files

- Group related declarations: type, constructor, methods together.
- Order: package doc, imports, constants, types, constructors, methods, helpers.
- One primary type per file when it has significant methods.
- Blank imports (`_ "pkg"`) only in `main` and test packages, so side effects sit at the program root instead of hiding in library code.
- No dot imports in library code. They hide where a name comes from.
- Unexport aggressively. You can export later; unexporting is a breaking change.

## Strings and conversions

- `strconv` for simple conversions, `fmt.Sprintf` for compound formatting.
- Use `%q` for string values in error messages, so empty strings and spaces stay visible.
- `strings.Builder` in loops, `+` for one-off concatenation.
- Prefer a narrow explicit conversion. Use generics instead of `any` when a concrete type will do: `func Contains[T comparable](s []T, want T) bool`.

## Philosophy

- A little copying is better than a little dependency.
- Use `slices` and `maps` from the standard library.
- Reflection is never clear. Avoid `reflect` unless the task needs it.
- Do not abstract prematurely. Extract when the pattern is stable, not when it looks like it might repeat.
- Minimize public surface. Every exported name is a commitment.

## Marking a deliberate override

A rule override gets no explanatory comment by default. [coding-rules](../../coding-rules/SKILL.md) allows one short line only when the code cannot show the point: an invariant, a contract, or a non-obvious why. A deliberate shortcut with a known ceiling uses the go-dev marker instead:

```go
// ponytail: linear scan; index map if this grows past ~100 items
```
