# Stage structure

Use this when a stage grows, when you add a stage file, or when someone proposes generics, wrapper structs, or per-domain types for the stage.

## Stage file layout

Order declarations in `*_stage_test.go` by the `coding-rules` File structure, like any Go file.

## One flat stage

When a suite covers several domains:

- Keep one flat `stage` struct with all state: core fields (`T`, `require`) and every domain's fields. Do not split state into per-domain structs, wrapper structs, or a composite fixture.
- Keep one constructor, `newStage(t)`, in the base stage file. It builds the whole struct. Partial or per-domain constructors leave core fields nil.
- Every fluent method is `func (s *stage) ... *stage`, in the file of its domain. Mixed-domain chains and `.and()` then work with no changes at the call sites.
- Put a builder where its state lives: used by two or more domains, in the base file; used by one domain, in that domain's file.
- Name files as exact-stem pairs: `X_test.go` and `X_stage_test.go`. A domain stage file holds only methods on `*stage` (no struct, no constructor). Delete a stage file with no methods.
- One domain per test file. Count which stage methods each test file calls. When a file mixes domains, split it by feature. Setup shared by many files (server start, fixture files) stays in the base stage file. Assertions stay in their domain.
- Do not let the base stage embed domain types while the domain types embed the base. That cycle reads as a structural error.
- Rename files with `git mv`, then grep `*.go` and `*.md` for the old stem. Gates do not catch stale names. Fold a small same-domain test file into the primary file of its pair instead of keeping two stems for one domain.

## Fluent-chain shape

A fluent chain works only while every method returns the same concrete type. One struct holds all state, and every method has a `*stage` receiver and returns that pointer.

- Do not make `stage` generic (`stage[S]`). A method from another domain breaks the typed chain, and a `*stage` receiver cannot soundly return a domain-typed `S`: the zero value is nil and panics downstream.
- Do not add per-domain wrapper structs (`type orderStage struct { stage }`). A stateless wrapper adds a constructor and no behaviour. Delete it when the state is already flat.
- Go 1.27 generic methods do not change this. A generic method on the base type cannot return the outer domain type either, because Go has no self type.
- To check a new shape, scratch-compile it: a throwaway module with the struct, the constructor, and the longest mixed-domain chain. Get agreement on that one probe file before you rewrite a whole suite.

## Delete dead stage code

Before you hand off a change, delete every stage method, fixture, and helper with no caller.

- Grep each removed symbol. Zero hits means it is gone.
- Do not keep dead methods alive with `var _ = []any{(*stage).foo}` blocks or `var _ = time.Time{}` lines. Delete the block, let the `unused` linter name the dead methods, then delete them.
- A helper kept for later costs upkeep now. Adding it back later costs less.

## Comments in stage files

Stage code carries almost no comments. The chain is the documentation.

- Delete requirement-tracker blocks, migration history, and `// moved from X` banners. That context belongs in the PR description.
- Keep one line only for a contract the name cannot carry, such as why a poll replaces a sleep.
- If a test needs a paragraph to be understandable, improve the method names or add a stage method.
