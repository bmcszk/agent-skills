# Modern Go

Use this when you bump the Go version, run `go fix`, pick a stdlib API, or touch JSON tags. It lists only what a model does not apply by default. Checked against go1.27.

## Version gate

- Never use a stdlib API newer than the `go` directive in `go.mod`. From Go 1.27, `go test` runs the `stdversion` vet check and fails. Bump the directive on purpose, or use the older API.
- Hand-modernize only code you touch, unless the task is a modernize pass. Running `go fix` on each package you changed is expected before handoff, even when it rewrites nearby lines.

## `go fix`

1. Preview: `go fix -diff ./<pkg-dir>`.
2. Apply: `go fix ./<pkg-dir>`.
3. List fixers with `go tool fix help`. Read one with `go tool fix help <name>`. Turn one off with `-<name>=false`.

Gotcha: the `omitzero` fixer removes `omitempty` from struct-typed fields. The `encoding/json` v1 output stays the same, because v1 never omitted structs. It does not add `omitzero`. Adding `omitzero` changes the API output, so treat it as a contract change. On `time.Time`, `omitempty` never omits.

## JSON

- `encoding/json` keeps v1 behaviour in Go 1.27.
- A move to `encoding/json/v2` is a contract change. It needs contract tests first. Differences:
  - field names match case-sensitively
  - nil slices and maps encode as `[]` and `{}`
  - `omitempty` has a new meaning
  - duplicate keys and invalid UTF-8 are errors
  - map key order is random
  - HTML characters are not escaped
  - byte arrays encode as base64

## UUID

- Stdlib `uuid` (1.27) has `New`, `NewV4`, `NewV7`, `Parse`, `MustParse`, `Nil`, `Max`. It has no v3 or v5 and no `sql.Scanner` or `driver.Valuer`.
- Keep `github.com/google/uuid` where code uses `uuid.NewSHA1` (v5 event IDs).
- Use `NewV7` for new time-ordered database keys.

## APIs to prefer (version added)

| Instead of | Use | Go |
|---|---|---|
| `errors.As(err, &target)` with a declared var | `target, ok := errors.AsType[*MyErr](err)` | 1.26 |
| a `ptr(v)` helper | `new(v)`, for example `new(30)` | 1.26 |
| `wg.Add(1); go func(){ defer wg.Done() ... }()` | `wg.Go(func(){ ... })`, only for goroutines that cannot fail, cannot panic, and need no cancellation. Otherwise `errgroup`. | 1.25 |
| `filepath.Clean` plus a prefix check on user paths | `os.OpenRoot(dir)` and `root.Open(name)`. It also blocks symlink escape. | 1.24 |
| `runtime.SetFinalizer` | `runtime.AddCleanup` | 1.24 |
| `strings.LastIndex` plus slicing | `strings.CutLast`, `bytes.CutLast` | 1.27 |
| hand copy of `url.Values` | `url.Values.Clone()`, `URL.Clone()` | 1.27 |
| fan-out `slog` handler code | `slog.NewMultiHandler` | 1.26 |
| `httputil.ReverseProxy.Director` in new code | `ReverseProxy.Rewrite` | 1.26 |

Generic methods (1.27): a method can declare its own type parameters, but such a method cannot satisfy an interface.

Timers (`go` directive 1.23 or newer): unused timers and tickers are collected without `Stop()`, and timer channels are unbuffered. Old drain-after-`Stop` code is not needed.

## Tests

- `t.Context()` (1.24) in place of a hand-made cancel context.
- `for b.Loop()` (1.24) in place of `for i := 0; i < b.N; i++`.
- `t.ArtifactDir()` (1.26) for files a test keeps.
- `synctest.Test(t, func(t *testing.T){ ... })` for fake time. `synctest.Sleep` (1.27) waits until the bubble is idle.
- `httptest.NewTestServer(t, handler)` (1.27) closes itself at test end. The first argument is `t`.

## Runtime and build

- Go 1.25 or newer sets `GOMAXPROCS` from cgroup limits. Remove `go.uber.org/automaxprocs`. Keep `GOMEMLIMIT` only when it matches a real memory limit.
- Before a bump to 1.27, grep `go.mod` and `//go:debug` lines for these removed GODEBUG keys: `asynctimerchan`, `tlsunsafeekm`, `tlsrsakex`, `tls3des`, `tls10server`, `x509keypairleaf`, `gotypesalias`. An old value fails the build.
- Go 1.27 tracebacks show pprof goroutine labels. Set `GODEBUG=tracebacklabels=0` when labels hold sensitive data.
- After a bump to 1.27, `go mod tidy` merges `require` blocks into one direct and one indirect block. Expect that diff.
- `/debug/pprof/goroutineleak` (1.27) finds goroutines blocked forever on a sync primitive.

## Tools

- Tools pinned in `go.mod` (1.24): `go get -tool <pkg>@<ver>`, then `go tool <name>`. Use this only when the repo does not pin tools another way.
- `go tool govulncheck ./...`, or `-mode=binary` on a built binary.
- `go doc -ex <pkg>` shows examples. `go tool doc` was removed.
- golangci-lint v2 has a `modernize` linter. Migrate a v1 config with `golangci-lint migrate`.
