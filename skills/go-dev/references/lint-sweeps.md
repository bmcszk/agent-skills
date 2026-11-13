# Lint sweeps

Read when a lint sweep spans many files, when findings repeat across
rounds, or when verifying a sweep someone claims is done.

## The laws

- Findings are absorbed by real fixes only. A config exclusion or a
  suppression marker reaching zero is cheating, and encoding a
  tolerance decision as an exclusion is the same cheat.
- Re-categorize the finding counts at the start of every round: the
  tree drifts while the sweep runs, so yesterday's counts are not
  today's baseline.
- A green-gates report from a delegated sweep is a hypothesis until
  recounted. Run the linter, tests with `-count=1`, vet, and the
  formatter yourself, diff the lint config against its baseline (the
  empty config diff is part of the gate), and run the mechanical
  re-scan across the whole file set - a per-file verdict list is a
  claim, the independent scan is the gate. Spot-read the files
  reported clean: a sweep can stamp verdicts while breaking the same
  rule class it lists.
- Prove zero behavior change before closing, not just green tests:
  diff run/pass/skip counts against the pre-sweep baseline. Green
  output with a lower pass count means assertions were deleted, not
  code moved.

## The two traps that cost real time

- A golangci build with a plugin linked in can silently drop findings
  in real multi-file packages that the vanilla binary at the same pin
  reports, while a canary in a tiny probe module still passes: the
  tiny module flags, the real package stays blind. Reproduce any CI
  finding with the vanilla binary (repo pin, config minus the custom
  block), and fix the code so both binaries agree. The durable setup
  runs the vanilla binary at the pin plus the house checker as a
  separate `go vet -vettool` pass.
- A test failure with produced-vs-expected mismatch is diagnosed
  against the test's own oracle before suspecting the code under
  test: check whether the probe drives all the state transitions
  (for example a removal after each mutation) before suspecting the
  container. Isolate third-party library semantics in a throwaway
  scratch module importing the repo's pinned version; probe code
  stays out of the repo.
