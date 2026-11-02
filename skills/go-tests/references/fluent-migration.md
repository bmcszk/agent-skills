# Migrating a Go test suite to the fluent stage DSL

Use when an existing Go test suite moves to the fluent given/when/then stage pattern from [fluent-stage-tests.md](fluent-stage-tests.md). Read that file first; it owns the target style (stage struct, `newStage(t)`, `.and()` at the end of a line, all state on the stage).

## Procedure

1. **Baseline and inventory.** Run the full suite with a JUnit report and count `<testcase>` entries (subtests included): that number is the parity bar for the whole migration. Grep the tree for the assertion dictionary (`assert.\|require.` plus method name, sorted and counted) to size the DSL surface you must cover. Read the lint config before writing anything: `testpackage` forces external test packages, `thelper` requires `t.Helper()` in helpers, and file or function length limits cap batch size.
2. **Track the work.** One tracked item per batch, chained so the next batch starts only after the previous closes. The binding decision (DSL surface, file layout) lives in the tracking item body, not in chat.
3. **DSL core first.** Add the stage struct, the constructor returning three stages, `.and()`, and the first given/when/then methods in a `*_test.go` file in the package directory. Verify build, vet, lint, and an unchanged full-suite count before migrating anything.
4. **Batch = one legacy source file.** Rewrite its tests as fluent scenario functions with names preserved, extending the DSL only when parity demands it. Delete the legacy file and its call sites in the same batch so the compile gate proves nothing was orphaned. Run all gates, commit, next batch.
5. **Closure.** All batches terminal: grep for the legacy pattern returns zero hits, wrapper files are gone, full suite green, and the final record captures before/after test counts plus any residual gaps.

## Pitfalls

- **CWD is the package directory under `go test`.** Fixture paths that resolve from the repo root break the moment tests move; probe with a temp test printing the working directory before mass-moving files.
- **Suffix the DSL file `*_test.go`.** A helper file without the suffix compiles but the runner reports "no tests to run" - a silent false green for the whole migration.
- **Count testcases, not tests.** Runner summaries and JUnit counts can diverge from mental sums; subtests count. Any post-batch delta needs a named explanation (documented new subtests), else treat it as lost assertions.
- **Field and method name collisions.** A `requestCount` method forbids a `requestCount` field on the same struct. Name the field differently and say why in one comment line, so the next extension does not "fix" it into a compile error.
- **Definitions-only files trip `unused`.** Until tests reference every method, reference the method set from a placeholder. But the placeholder masks dead DSL: a method with zero callers stays lint-clean while listed. Migration complete means deleting the placeholder and letting `unused` name the dead methods, then deleting them. Never hand-maintain reference lists; the linter already does that job and cannot drift.
- **Orphaned comment fragments in migrated files are deletions, not rewrites.** Files that went through partial cleanups carry mid-sentence comment fragments above test functions. Delete them whole - shrinking a fragment to one line preserves nonsense.
- **Extend, never bypass.** Missing assertion? Add a fluent method following the stage conventions. A single direct helper call inside a test function re-opens the old style; reject it in review.
- **Mid-migration layout changes go to the batches still queued, not to finished ones.** Finished batches already passed their gates; rewriting them re-runs the whole migration.
