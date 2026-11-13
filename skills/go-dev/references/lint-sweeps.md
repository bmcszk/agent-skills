# Lint sweeps

Read when a lint sweep over complexity, structure, or style findings
spans many files, when the same findings repeat across rounds, or when
verifying a sweep someone else claims is done.

## The sweep loop

1. Baseline: run the linter over the tree, redirect findings to a
   scratch file, and count them by category (test-package, complexity,
   other) with a small filter script. Totals drift while the sweep
   runs, so re-categorize at the start of every round.
2. Findings are absorbed by real fixes only. A lint config exclusion or
   a suppression marker reaching zero is cheating, not fixing, and
   encoding a tolerance decision as an exclusion is the same cheat.
   Production findings go first (`grep -v '_test.go'`), and test-file
   findings get real fixes too: test-package conversions and helper
   splits, never contorted helpers.
3. After each function split, run the touched package's tests for fast
   feedback. Full tests, vet, and the formatter run on the touched tree
   before each batch commit; a multi-edit batch reliably leaves
   formatting drift that fails gates later.
4. Commit in batches with the gate results in the message (build, vet,
   tests, remaining counts per category). Before closing the sweep,
   prove zero behavior change, not just green tests: diff run/pass/skip
   counts against the pre-sweep baseline (a temp worktree at the base
   commit is the easy way). Green output with a lower pass count means
   assertions were deleted, not code moved.
5. Check the CI failure surface (`gh run view <id> --log-failed`)
   before assuming local lint equals CI lint; the repair on either side
   is the same real fixes. Line-length stragglers appear from freshly
   wrapped calls: the formatter does not wrap strings or argument
   lists, so expect one more round of manual wraps and re-run the
   linter before committing.

## Recount the gates yourself

A green-gates report from a delegated sweep is a hypothesis until
recounted: run lint, tests with `-count=1`, vet, and the formatter on
the touched tree, and diff the lint config against its baseline (an
empty config diff is part of the gate). The same law covers style and
structure sweeps: run the mechanical re-scan (grep, AST, regex) across
the full file set before closing the sweep, because a per-file verdict
list is a claim and the independent scan is the gate. Spot-read the
files reported clean: style is not machine-checked everywhere, so a
sweep can stamp verdicts while breaking the same rule class it lists.

## Diagnose against the oracle first

When a test fails with a produced-vs-expected mismatch, diagnose
against the test's own oracle before suspecting the code under test:
check whether the probe drives all the container's state transitions
(for example, a removal sweep after each mutation) before suspecting
the container. The failing sequence usually pins the missing call, not
the data structure.

Keep a throwaway module in a scratch location (such as
`/tmp/<topic>-probe`) for isolating third-party library semantics
(entity reuse, iteration order): import the pinned version from the
repo's `go.sum`, replicate the exact operations, and print state per
step. Probe code stays out of the repo; the finding is what ships.

## Split patterns, picked by the offender's shape

- Row-parse loop (the usual complexity offender): a loop body of N
  sequential error checks becomes `parseXxxRow(row) (T, error)`; the
  loop keeps only parse, append, and early return. One move fixes
  cognitive and cyclomatic complexity together.
- Switch-on-string value mapping: a `map[key]value` lookup plus an
  explicit fallback return in the function, for pure value-per-key
  dispatch only.
- Flag-parameter findings on a boolean pair: the code stops branching
  on the bare bool. Encode the pair as its own tiny named type carrying
  its tag, or pass the two constants from the call site. The finding
  closes by restructuring, never by config exclusion or suppression.
- Dispatch switch in a reader or parser: split at the header/tag
  boundary. The outer function reads framing, a `decodeXxxPayload`
  helper returns `(n, error)` per tag or type, and the default branch
  becomes its own tiny validator.
- Argument-limit findings: bundle per-call state (callbacks plus scalar
  thresholds) into one small context struct passed as a single
  argument. Trimming helpers or shuffling parameters to dodge the
  counter is not a fix.
- Test-file complexity yields to per-case helpers, table subtests, and
  small named outcome types replacing boolean flag parameters.
  Assertions stay behavioral, and byte-identical test-run counts
  against the baseline are the verification.

## Testpackage to black box

A testpackage finding converts rather than splits:

1. Rename the file's package to `package X_test` and add a named import
   of the package under test.
2. Qualify every unqualified identifier (a regex pass over the file),
   then run `go vet`, which names each remaining undefined identifier.
3. Give the package minimal exported accessors for the unexported
   identifiers the tests poke, each with a real upstream analogue or
   parity role, verified against an outside-package consumer.
4. Watch the follow-on findings the new exports trigger: naming rules
   (fix by renaming the unexported internal so the exported name stays
   distinct), redundant import aliases (drop an alias equal to the
   package name), and dot imports (use named imports).
5. Identifiers that cannot be exposed without breaking the upstream API
   mapping become recorded residuals (identifier list plus reason),
   never forced and never excluded.

## Named returns and `:=`

In a function with named returns, `x, err := f()` fails with `no new
variables on left side of :=` because both names already exist. Assign
with `=`, and declare genuinely new locals only.

## Custom lint builds are not oracle-equivalent

A golangci build with a plugin linked in can silently drop findings in
multi-file real packages that the vanilla binary at the same pin
reports, while a canary in a tiny probe module still passes: the tiny
module flags, the real package stays blind. Before trusting a local
green on lint-sensitive diffs, reproduce any CI finding with the
vanilla binary (install at the repo pin, config minus the custom
block), and fix the code so both binaries agree. The durable setup runs
the vanilla binary at the pin with the house checker as a separate
`go vet -vettool` pass plus a seeded-violation canary that fails the
gate when the oracle goes blind.
