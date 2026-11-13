# golangci-lint config pitfalls

Read when wiring a custom linter into golangci-lint, when a version pin
or a config edit changes what gets reported, or when CI lint disagrees
with a locally green tree.

## Phase markers have no golangci linter

No golangci linter checks test phase markers, and `godot` fights them:
godot requires comments to end in a period, which marker lines do not.
Leave the markers to the house checker or review, and leave `godot`
disabled in a repo that writes marker-structured or fluent tests. The
enforcement route for a house rule that needs a real checker runs
outside the golangci build: a custom checker driven as a separate
`go vet -vettool <analyzer>` pass, pinned as a proxy module in the lint
oracle. That is the zero-rebuild route when a rule must stay out of the
golangci binary and config.

## Custom checker routes, ranked

The upstream ranking is the one to follow: module plugin system first,
shared-object plugin only where a custom binary cannot be built.

- The golangci-lint GitHub action (v9 and later) detects
  `.custom-gcl.yml` automatically, builds the custom version, and runs
  it: a hand-written CI build step for the custom binary is dead
  weight.
- `go get -tool <cmd>@vX` plus `go tool <name> ./...` (Go 1.24 and
  later) is the route with no YAML at all: the version lands in
  `go.mod`, the checksum in `go.sum`, and the tool exits 3 on findings.
  Use it when the repo wants a single checker instead of a lint suite.
- Shipping the merged binary is a legitimate peer pattern.

## The version pin lints the tag, not the tree

A repo pinned to an old tag keeps retired rules and reports code
against a rule set that is no longer current, so a green pin can be
green against retired rules. Bump the tag and rebuild together; the
config field stays optional when the command carries the version
(`golangci-lint custom --version vX`), which keeps one pin instead of
two.

## Sibling naming rules fire in one pass

A revive naming rule has siblings imposing suffix rules on neighboring
time-typed locals, so fixing only the line CI flagged passes round one
and re-fires round two. When any naming rule fires: grep the package
for every variable the rule and its siblings could touch, satisfy all
sibling suffix rules in one edit, then run the linter on just that
package with the repo's real config before pushing. One CI round, not
one per rule.

## gh triage and the `--jq` number gotcha

```bash
gh run list --branch <branch> --limit 3 \
  --json databaseId,status,conclusion,displayTitle
gh run view <run-id> --log-failed | grep -E "FAIL|Error|error"
```

`databaseId` is a number in gh's JSON. In `--jq`, use string
interpolation `"\(.databaseId) \(.conclusion)"`; `number + string`
concatenation errors the entire query with a confusing type error
instead of results. `--log-failed` returns only the failed steps' logs;
grep it for the rule name and the flagged `file:line:col`, since the
messages name both.

## testdata is invisible to self-linting

Fixtures under `testdata` are skipped, so a linter cannot self-check
its own `analysistest` fixtures through golangci-lint even when enabled
on itself. Prove it before wiring self-linting: plant a broken fixture
under `testdata` and one at the root, and compare which gets reported.
Self-checking belongs on `go vet -vettool`, which sees them.

## Shipping a config example

- Copy the bytes, never retype. Reading a config through a truncated
  read and writing the tail from inference yields a plausible file with
  invented settings. Regenerate programmatically (read the source,
  prepend the header, write) and diff the body against the original to
  prove identity before committing.
- `golangci-lint config verify` is necessary, not sufficient: it checks
  the schema and says nothing about whether the custom linter loads.
  Build the custom binary from the example pair in a scratch module
  containing a deliberately broken test, and confirm the plugin's
  diagnostic appears alongside the stock linters' output.
- Name examples by the axis they answer: route-comparison examples
  answer "which route", a whole working config answers "what does a
  real one look like", and the name says which is which.
