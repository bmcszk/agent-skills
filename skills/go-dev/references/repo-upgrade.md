# Repo upgrades: directives, toolchains, dead code

Read when bumping the go directive or toolchain pins across a repo,
or when deleting dead code at scale. Each law below came from an
upgrade that passed `make check` and still broke or misled.

## The directive floor may be owned by a dependency

The `go` directive floor can be owned by a transitive dependency:
hand-lowering it is silently reverted by the next `go mod tidy`.
Find the owner with `go list -m all` sorted by reverse version
(`go list -m all | sort -rV | head`) and bump the owning module, not
just the directive.

## Align every toolchain consumer in one commit

CI go-version, containerfile golang image, and helm version
overrides are separate toolchain consumers: align them in the SAME
commit. A stale pin fails only in that consumer - green `make check`
locally proves nothing about the container build, and the failure
surfaces later in the one pipeline nobody watched.

## Bump test-only dependencies explicitly

`go get -u` misses test-only dependencies: nothing in the build
graph references them, so they stay pinned while everything else
moves. List and bump them explicitly in the same change.

## Run the dockerized e2e after any directive bump

Run the dockerized e2e suite once after any directive bump even when
`make check` is green: the image pins its own toolchain, and a
directive the host toolchain accepts can break the image's older
one.

## Triage gofmt -l before reformatting

Run `gofmt -l` on clean master before reformatting anything: a repo
whose lint gate excludes gofmt has pre-existing offenders that bury
the real diff. Fix formatting only in files the change already
touches; reformatting the pre-existing offenders turns a review of
the upgrade into a review of noise.

## Deleting dead code raises measured coverage

Deleting dead code raises measured coverage on its own: the removed
lines were never executed, so removal deflates the denominator.
Quote that effect as the selling point of the deletion instead of
letting a coverage jump read as new tests.

## Grep all trees before deleting an interface family

Grep all trees (services, charts, docs, scripts) for an interface's
symbols before deleting the family: the last consumer is often a
config template or a doc example, not Go code, and the compile step
cannot testify for those.

## Mass sed double-stars pointers

Mass sed replacement over pointer receivers and channel types
double-stars `*T` into `**T` and breaks consumer-side sibling types
that share the symbol. Replace per declaration with a reviewed diff,
or run the replacement and then compile-verify every package that
mentions the symbol.

## Trace chart and doc config end to end

A config key added to a chart or doc travels render -> ConfigMap ->
mount -> env -> loader. Templates render for config no loader opens:
trace each hop in the running system (rendered manifest, mounted
file, process env) before claiming the setting works.
