---
name: port-parity-testing
description: Use when porting code with parity tests against a reference implementation - what parity pins, which oracles are legal, fixture discipline, and differential testing in containers.
license: MIT
metadata:
  audience: developers
  workflow: testing
  category: dev
  technologies: testing, differential-testing, containers
---

# Port parity testing

Parity pins BEHAVIOR, never SHAPE: fixture shapes, naming idioms,
and signature-mirror functions that exist only to look like the
upstream are violations. The port answers the same inputs with the
same outputs; it owes nothing to upstream's file layout.

## Oracles

- An oracle must not re-derive the implementation's arithmetic:
  copying the port's formula into the test makes the test pass when
  the port is wrong twice the same way. Tables carry literals;
  a differential oracle exists only in the randomized layer, where
  port and reference run side by side on generated inputs.
- Read the upstream ENCODER's emission table to define the opcode
  set: the decoder alone omits the cases the encoder never
  produces, and the parity corpus inherits that blind spot.
- Derive checker semantics from the upstream reference FILE, never
  from the port's own docs: docs describe intent, the reference
  defines behavior.

## Fixtures

- Commit fixture bytes and their manifest: env-gated upstream reads
  make CI vacuously green (no fixtures means no comparisons, which
  passes).
- Count lines with `awk 'END{print NR}'`, not `wc -l`: a file
  without a trailing newline undercounts, and a count assertion
  built on it passes on truncated fixtures.
- Golden digests prove nothing about opcode boundaries the corpus
  never reaches: hand-craft frames exercising both sides of each
  boundary.
- Output-orientation parity hides from digests: same digest,
  different internal state. Pin it with asymmetric fixtures (inputs
  that differ, outputs that must match).

## Differential runs

- Scripted RNG tapes with independent line-by-line traces: when the
  runs diverge, the trace names the exact line, and a shared
  transcript cannot.
- In containers: a golden sequence, a seeded lockstep reference, and
  edge rows run in one compose file so both images see the same
  bytes.
