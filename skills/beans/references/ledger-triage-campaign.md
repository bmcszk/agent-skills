# Ledger-scale triage campaign

Read when triaging a whole ledger (every open entry at once) or
auditing a wave of closures. Ledger scale breaks the one-entry
workflow in specific ways; this is the campaign recipe and the laws
its steps carry.

## Shape of the campaign

- Batched read-only child wave: children of roughly four entries
  each, bounded wall time per child, driven by a marker-gated
  resumable driver so an interrupted wave restarts at the last
  marker, not at entry one.
- The parent is the sole writer: children report findings, the
  parent edits. Two writers on one ledger entry race and the loser's
  correction silently vanishes.
- Follow the fix pass with an independent verification wave and
  budget for a meaningful wrong-finding rate: the fixers and the
  verifiers must not share assumptions, or the verification
  rubber-stamps the same error twice.
- The ledger linter is the gate: no entry leaves the campaign while
  the linter reports it.
- Harden open questions into stamps: an open question that survives
  a campaign becomes a definite checked state or it re-opens the
  same debate next campaign.

## Stamps never outrun edits

A fix note describing the correction is not the correction: the
operative body text must change in the same pass, and a later wave
must prove the change landed. A stamp recorded while the body still
reads the old way produces a ledger where every record claims a fix
and nothing is fixed.

## Session-resume reconciliation

On resume, reconcile stale in-progress claims against merged
history before continuing: sweep same-title duplicates (a resume
that re-creates entries doubles the wave), read the landed-as
verdict for each claimed entry, and cite `git log -S` on the entry's
key symbol when the ledger record and the history disagree. The
ledger is a claim about history; history wins.
