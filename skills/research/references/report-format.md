# Report format

Load before writing the final report.

## Skeleton

```markdown
# <Question as title>

## Overview
<3-6 sentences: direct answer first, then scope. For comparison reports
use a criteria table with a verdict row; for fact-checks an evidence
for/against table; for how-tos the numbered step overview.>

## <Section per sub-question>
<Findings with [N] citations and evidence labels inline.>

## Contradictions
<Each disagreement: source A says X [1], source B says Y [2]; why they
may differ. No silent arbitration.>

## Gaps
<Each unanswered or thin sub-question and what was tried.>

## Sources
| # | Source | Tier | Accessed |
|---|--------|------|----------|
| 1 | <title - url> | primary | 2026-11-02 |
```

## Laws

1. Direct answer in the first sentences; detail after.
2. Every factual claim carries `[N]`; every material fact keeps its
   `[VERIFIED]` / `[SOURCED]` / `[REASONED]` / `[ESTIMATED]` label.
3. `[REASONED]` and `[ESTIMATED]` claims read as indicative (likely,
   suggests), never as hard fact.
4. Freshness-sensitive numbers carry an as-of date.
5. Snapshot citations read "as archived <date>".
6. If synthesis failed, compile raw findings grouped by sub-question with
   labels and state that synthesis was not completed.
7. End with a stats line: rounds, queries, URLs fetched, sources cited.

## Category hints

| Category | Overview shape |
|---|---|
| comparison | criteria table + verdict row |
| product | ranked list, pros/cons, top pick |
| how-to | numbered steps; sections cover prerequisites and pitfalls per step |
| fact-check | for/against evidence table + verdict |
| explainer | key findings simple to deep |
| factual | numbered key findings |
