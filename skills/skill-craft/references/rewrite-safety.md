# Rewrite safety

Read when a pass replaces whole sections of a skill or doc file, merges
or dedupes rules, or compresses prose. A compact rewrite is the
standing opportunity for silent loss: the edit lands, the diff looks
clean, and rules disappear inside the replaced span.

## Inventory before replacing

Before replacing everything between heading A and heading B, list the
headings between them and confirm each survives or is intentionally
dropped. After any merge or dedupe pass, grep the touched section
names: a heading appearing twice means the splice stitched two copies.

## Account for every line

Verify content survives, not just that the edit landed. Account for
every deleted line as kept, moved, or intentionally cut in a
kept/moved/cut ledger. A word probe with the old phrasing reports
false misses on reworded lines, so the ledger is the check and grep is
not.

## Replace-with-anchor edits

The anchor in a replace-with-anchor edit is the first occurrence of the
text, so anything sitting between two occurrences vanishes inside the
replaced span. Diff the deleted lines against the prior state and
account for each before committing; a heading count plus a rule count
against the old file catches what the diff looks like it kept.

## Keep the qualifiers and the examples

A plain-language or compression rewrite keeps the qualifiers and worked
examples that carry rule content ("or section", "at that level", a
named example). Cutting them reads cleaner and silently weakens the
rule: the qualifier was the rule's boundary, and the example was its
proof.

## Validate old against new

Dispatch the old and new text to a fresh reviewer together and request
dropped rules, invented rules, and meaning drift as separate findings;
patch every finding before the rewrite ships, rather than as a
follow-up commit.

## Scoped removal is delete-only

When the request names what to remove, deleting exactly that (plus
anything it orphans) is the deliverable. Upgrading a removal into a
refactor, helper extraction, reorder, or rename is a bigger change than
the one asked for and reads as ignoring the instruction; the cleanup
gets offered separately, in its own commit.

## State the law positively

Rules, comments, and docs state what is done or required. Removal
narration and annotation-in-place both grow the file instead of
shrinking it: a fact documented elsewhere is deleted, and the removal
carries no explanation in its place.

## Fixes stay fixes

A sweep that cannot reach zero honest findings closes with real fixes
(convert, split, restructure). Absorbing a finding class into a lint
config exclusion is the same cheat as a suppression marker, even when
framed as encoding a prior decision; a finding that cannot be fixed
without contortion goes to the user for an explicit recorded ruling on
the config.
