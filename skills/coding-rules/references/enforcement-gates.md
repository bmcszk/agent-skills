# Enforcement gates for delegated rule passes

Read when coding rules are enforced through delegated passes: worker
waves that classify, fix, or verify rule findings across a repo.
Each gate below exists because skipping it once produced a sweep
that looked done and was not.

## Ground every rule in example pairs

Each enforced rule carries a compliant/violating example pair drawn
from the target repo's own code, not from prose description. Workers
classify by pattern match against the pair; a prose-only rule
("functions read as intent") produces verdicts that vary by
interpreter, and the variance shows up when two workers disagree on
the same file.

## Write the keep-list before any deletion pass

Before a comment-deletion or pattern-purge pass, write the
keep-list: the citation sites the rules legitimately quote. A purge
that deletes the citation class destroys the rule's own evidence,
and the loss is information, not cleanup - the rules file's examples
then point at code that no longer exists.

## Audit per batch at land time

Audit each landed batch when it lands, not in one end-of-sweep pass:
a wrong verdict discovered at the end invalidates every batch built
on top of it, while a wrong verdict caught at land time costs one
batch.

## Verdicts carry evidence

Every FIXED verdict cites the rule id plus `file:line` of the
correction. A bare "fixed" is unverifiable, and unverifiable
verdicts pass the sweep while the violation survives.

## Sweep shape: all rules, all files, one matrix

Run the sweep all-rules-x-all-files with a per-file verdict matrix
as the deliverable. For every violation class the matrix misses,
build a mechanical scanner (grep or linter rule) that detects it and
rerun. A user-falsified all-clean claim voids the task: the
scanner, not the worker's confidence, is the evidence of coverage.

## Category-order gate after reorders

After a pass reorders declarations (per the file-layout ranking),
rerun the category-order scanner: hand reordering reintroduces
adjacent-category violations at the edit seams, and only the scanner
sees them.

## Scope widening enters with its scanner

A new violation class discovered mid-sweep enters the contract with
its scanner before the rerun, never as narrative in the final
report. A class named but not scanned is a class the rerun still
misses, and the report then claims coverage the contract does not
define.
