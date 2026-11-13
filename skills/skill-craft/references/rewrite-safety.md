# Rewrite safety

Read when a pass replaces whole sections of a skill or doc file,
merges or dedupes rules, or compresses prose. A compact rewrite is
the standing opportunity for silent loss: the edit lands, the diff
looks clean, and rules disappear inside the replaced span.

- Before replacing everything between heading A and heading B, list
  the headings between them and confirm each survives or is
  intentionally dropped. After a merge pass, grep the section names:
  a heading appearing twice means the splice stitched two copies.
- Account for every deleted line as kept, moved, or intentionally cut.
  Grep with the old phrasing reports false misses on reworded lines;
  the ledger is the check, not grep.
- The anchor in a replace-with-anchor edit matches the first
  occurrence, so content sitting between two occurrences vanishes
  inside the replaced span. Diff the deleted lines and account for
  each before committing.
- A plain-language or compression rewrite keeps the qualifiers and
  worked examples that carry rule content: the qualifier was the
  rule's boundary, the example was its proof. Cutting them reads
  cleaner and silently weakens the rule.
- Dispatch the old and new text to a fresh reviewer together, asking
  for dropped rules, invented rules, and meaning drift as separate
  findings; patch every finding before the rewrite ships.
- When the request names what to remove, deleting exactly that (plus
  what it orphans) is the deliverable. Upgrading a removal into a
  refactor or reorder exceeds the instruction; the cleanup is offered
  separately.
- A sweep that cannot reach zero honest findings closes with real
  fixes. Absorbing a finding class into a lint config exclusion is
  the same cheat as a suppression marker; an unfixable-without-
  contortion finding goes to the user for a recorded ruling.
