# Core Go rules

Use this as the baseline for Go implementation and review work.

Read `development-balance.md` first. The rules below are grouped by lens so you can see what is a safety rule, what is repo convention, what is general practice, and where YAGNI applies.

## Always: safety and correctness

Never YAGNI these away:

- Always check errors.
- Wrap errors with useful operation context using `%w`.
- Use `errors.Is` and `errors.As`; do not compare errors with `==` except for `nil`.
- Collect independent validation errors with `errors.Join`, so the caller sees all of them.
- Do not use `panic` for normal error handling.
- Pass `context.Context` as the first parameter for operations that can block or cross process boundaries.
- Do not store `context.Context` in structs.
- Do not add `//nolint` or `//revive` comments. Fix the issue or narrow the code.
- Do not delete or skip tests to make checks pass.
- Check the error of `Close()` and `Flush()` on files, writers, and transactions you write to. A dropped error there loses data silently. A plain `defer f.Close()` is fine for read-only resources.
- After a loop over `sql.Rows` (also inside an iterator), check `rows.Err()`. The loop ends the same way on success and on a broken connection.
- A typed nil pointer stored in an interface is not `nil`. Return a literal `nil` for "no error", never a nil `*MyError`.
- Guard a map shared by goroutines with a mutex. Concurrent map writes crash the program.

## Repo consistency: follow the repo

Prefer existing repository patterns over generic advice:

- Match nearby packages for naming, file layout, error messages, and test style.
- Keep edits small and close to the code that owns the behavior.
- Define interfaces at the consumer, in the same file as the struct or constructor that needs them. Keep them small: only the methods that consumer calls.
- Do not create `interfaces.go` or separate interface packages for convenience.
- Accept interfaces and return concrete types unless the repository has a different established pattern.
- Do not add an interface only so a test can swap the dependency. Unit tests use no mocks, so the interface has no real consumer.
- Deterministic event IDs (UUID v5, `uuid.NewSHA1`): the namespace UUID is a fixed random value per record type and never changes once shipped. It is not a hash of the type name. Build the hashed name from stable fields, for example `eventType-recordType-recordID-version`.
- Use `errgroup.WithContext` when goroutines can fail. Set `SetLimit` when fan-out is unbounded or input-sized.
- Avoid bare `sync.WaitGroup` when errors matter.
- Keep public code near the top of files and private helpers lower down. Prefer [coding-rules](../../coding-rules/SKILL.md) File structure over copying a disordered sibling file.
- Use the repository runner (`just`, `make`, or existing scripts) for build, lint, and test commands.

## Good practices: when the repo has no stronger local pattern

- Run `gofmt` after editing Go files.
- Use `gopls` diagnostics when available.
- Run focused tests for the changed behavior. Run `-race` for concurrent code.
- Run the lint target before finishing when the repository has one, or record the blocker.
- Put commands under `cmd/<binary>`, application code under `internal/`.
- Create a package only for a real boundary, not for layer jargon.

### Style

- An `if` with 3 or more operands gets named booleans (`isExpired := ...`), so the condition reads as a rule. Keep an expensive last operand inline, so short-circuit still skips it.
- Assign a default, then override it in a `switch`. An `if / else if / else` assignment chain hides which value is the default.
- More than 4 parameters: group them in an options struct. Wrapping the line does not fix a long signature. A call that still breaks lines puts one argument per line.
- Pass a pointer only to mutate, when `nil` has a meaning, or for structs of about 128 bytes or more. A `*string` does not save memory.
- Format string values in error messages with `%q`, so empty strings and spaces stay visible.
- Blank imports (`_ "pkg"`) only in `main` and test packages, so side effects stay visible at the program root.
- Initialize a slice that reaches JSON (`[]T{}`), because `encoding/json` encodes a nil slice as `null`. Preallocate capacity only when the size is known, not on a guess.
- A sub-slice keeps the whole backing array alive. Copy the part you keep when the source is large and short-lived.

### Design

- Constructors take plain arguments. Use functional options only when the repo already does. An option that can fail returns an `error`, so bad config fails at construction.
- The zero value of an enum is `Unknown` or invalid. Otherwise an unset field silently passes as the first real member.
- Copy the layout of a sibling service. Do not pick an architecture style (clean, hexagonal, DDD) or add `handler/service/repository` layers by code size.
- Use `runtime.AddCleanup`, not `runtime.SetFinalizer`. The cleanup gets an argument, not the object, so there is no resurrection and cycles are still collected.
- Use generics for type-safe containers and algorithms that repeat across types. Use a concrete type for business logic, models, and handlers, and an interface when behaviour varies.

### Embedding

- Embedding promotes the embedded struct's members. Call them on the receiver (`c.require`), and do not re-bind the embedded value inside a method (`p := c.parts`). Bind it only when you pass it as a value.
- Shape embedding one way: a composite embeds state structs, and state structs hold fields only. A cycle (base embeds parts that embed base) compiles but reads as a structural error.
- An empty marker struct that exists only for a layout rule fails the `unused` linter. Give it the real fields its methods write, or delete it.

## YAGNI: minimalism within the above

Apply only after the rules above are satisfied:

- Do not introduce broad abstractions unless they remove real local complexity now.
- Do not add a new dependency if stdlib or an existing dependency covers the need.
- Do not add configuration for a value that never changes.
- Do not create shared `types`, `utils`, or `helpers` packages for one caller.
- Do not add unit tests with mocks. Use integration or E2E tests for dependency behaviour instead.
- Prefer one clear function over a small hierarchy of wrappers.
- When choosing between two valid approaches, pick the one with the smaller diff and fewer new concepts.

When a deliberate simplification has a known ceiling, mark it with a `ponytail:` comment and name the upgrade path.

## Review filter

Before proposing or applying a change:

1. Does this follow the repo and its sibling services?
2. Is it idiomatic and defensible engineering practice?
3. Is it the smallest readable change that solves the problem?
4. Active-row checklist: when the diff changes a cap or what counts as active or in-flight, list every path that moves a row out of that set (success, fail, timeout, stuck detection, not found). For each path, say whether it frees the slot or only logs or alerts.

If any answer is no, revise or explain the exception briefly.
