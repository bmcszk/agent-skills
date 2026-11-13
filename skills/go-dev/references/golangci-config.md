# golangci-lint config pitfalls

Read when wiring a custom linter into golangci-lint, when a version
pin or config edit changes what gets reported, or when CI lint
disagrees with a locally green tree.

- No golangci linter checks test phase markers, and `godot` fights
  them: godot demands periods on comment lines, marker lines do not
  carry them. Leave markers to the house checker or review, and leave
  `godot` disabled in a repo that writes marker-structured tests. The
  enforcement route for a house rule that needs a real checker is a
  separate `go vet -vettool <analyzer>` pass, not the golangci build.
- Module plugin system first, shared-object plugin only where a
  custom binary cannot be built. The golangci-lint GitHub action (v9+)
  detects `.custom-gcl.yml` automatically and builds the custom
  version: a hand-written CI build step for it is dead weight.
- A version pin lints the tag's rule set, not the current tree: a
  green pin can be green against retired rules. Bump the tag and
  rebuild together; reproduce a finding at the exact pin before
  trusting a local-only green.
- A revive naming rule has siblings imposing suffix rules on
  neighboring variables: fixing only the flagged line passes round
  one and re-fires round two. Grep the package for every variable the
  rule and its siblings touch, fix all in one edit, then lint that
  package with the real config.
- Fixtures under `testdata/` are invisible to golangci's
  self-linting; self-checking belongs on `go vet -vettool`, which
  sees them. Prove it by planting a broken fixture in both places.
- `golangci-lint config verify` is necessary, not sufficient: it
  checks the schema, not whether the custom linter loads. Build the
  binary from the example in a scratch module and confirm the
  diagnostic appears alongside stock output.
- In `gh run view --jq`, interpolate ids as strings
  (`"\(.databaseId) \(.conclusion)"`): number-plus-string
  concatenation errors the whole query. `--log-failed` returns only
  failed steps; grep it for the rule name and `file:line:col`.
