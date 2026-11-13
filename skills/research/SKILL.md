---
name: research
description: >-
  Use when a question needs multi-source web research beyond one search:
  deep dives, comparisons, fact-checks, tech or market scans, and cited
  reports. Runs an iterative plan-search-extract-synthesize loop with
  evidence labels, source tiers, gaps and contradictions. Not for single
  known-URL reads or one-shot lookups answered by the first search.
license: MIT
metadata:
  audience: developers
  workflow: research
  category: research
  technologies: web-search, content-extraction, archives
---

# Research

Deep research is a loop, not a search. Plan, then repeat
query-search-extract-synthesize until evidence covers the question, then
report with citations. Tools differ per runtime; the loop does not. Load
`references/tools.md` when invoking concrete search or fetch tools, and
`references/report-format.md` before writing the report.

## Step 1 - Plan

1. Restate the question as one sentence. If it is ambiguous, ask before searching.
2. Split it into 3-6 sub-questions that together answer it.
3. Classify the report: factual, comparison, product, how-to, fact-check, explainer.
4. Set the round cap by complexity: simple 2, moderate 3, complex 5. The cap is a ceiling, not a target.

## Step 2 - Date grounding

Inject the current date before any search. LLMs default to training-cutoff
years and query stale terms. Any query needing a year uses the current year.

## Step 3 - Iterative loop

Each round runs: gap queries, search, extract, synthesize, stop check.

### 3a - Gap-driven queries

1. Round 1 targets the sub-questions; later rounds target documented gaps.
2. Generate 2-4 queries per round. Never repeat a query that already returned results.
3. From round 2 on, include one counter-evidence query against the leading answer. Zero refutes usually means weak searching, not absence of dissent.
4. Prefer operator-enriched queries: quoted phrases, `site:` for official hosts, `filetype:pdf` for specs and papers, `-term` to cut noise, a time filter for freshness. See `references/tools.md` for the per-tool syntax.

### 3b - Search

1. Run one search per query, limit 8-10 results.
2. Empty result escalation: first empty, broaden keywords or synonyms; second consecutive empty, change domain, language, or angle; third, mark the sub-question a documented gap and move on.

### 3c - Extract with a quality filter

Discard before reading: thin landing pages, keyword-stub aggregators, login
walls without a preview, already-fetched URLs. Then per source:

1. Extract only goal-relevant facts; skip navigation and boilerplate.
2. Assign each unique URL a numbered citation on first encounter; reuse it after.
3. Tier the source: primary (official docs, filings, papers, pricing pages), secondary (tech press, analyst reports), tertiary (forums, wikis, aggregators). Tertiary never solely supports a material claim.
4. Fetch failures go down the recovery ladder in `references/tools.md` - Wayback, archive.today, API pivot, browser. Cite snapshots with their archive date. When a recovered page looks wrong, read `references/blocked-page-recovery.md` - the routes-that-lie catalogue and its detection heuristics.

### 3d - Evidence labels

Tag every material fact (statistic, date, relationship, causal claim, quote):

- `[VERIFIED]` - corroborated by 2+ independent cited sources
- `[SOURCED]` - one named source, uncorroborated
- `[REASONED]` - own inference, present as indicative, never as fact
- `[ESTIMATED]` - derived calculation or stated assumption

Corroboration during dedup promotes `[SOURCED]` to `[VERIFIED]`. Never
fabricate to fill a gap; an unanswerable sub-question is a documented gap.

### 3e - Synthesize into research state

After each round keep one cumulative state: per sub-question, status
answered/partial/unanswered, findings with citations and labels, then a gap
list. Deduplicate (cite the best or both for corroboration), surface
contradictions with both attributions instead of silently arbitrating.

### 3f - Stop check

Stop when every sub-question is answered or documented as a gap, the round
cap is reached, or counter-evidence was searched at least once. Budget
guard: past round 2, summarize earlier rounds aggressively instead of
carrying full extracts; favor synthesis over more gathering.

## Step 4 - Report

Write the report from the research state, not from memory. Load
`references/report-format.md` for the skeleton. Laws:

1. Inline citations `[N]` on every factual claim; source table with tier and access date.
2. Explicit Gaps and Contradictions sections; never hide them in prose.
3. Facts keep their evidence labels in the text.
4. If synthesis fails, compile the raw findings with labels and say synthesis was not completed - never output nothing when sources exist.

## Step 5 - Provenance

External facts get "as of" dates when freshness matters (prices, versions,
breaking news). A snapshot citation names the snapshot date. Unverified
inference stays labeled, never asserted.
