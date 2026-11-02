# Tools reference

Concrete tool incantations for the research loop. The body's laws are
tool-agnostic; this file maps each loop step to clients that may or may not
exist in a given runtime. Use the first available in each row; fall down the
row when a client is missing or fails.

## Search

| Capability | Clients |
|---|---|
| Built-in web search tool | `web_search(query, limit)` - supports `site:`, `filetype:pdf`, quoted phrases, `-term`, `intitle:` |
| SearXNG via mcpc | `mcpc @searxng tools-call searxng_web_search query:="..." time_range:="month" language:="en"` - params: `pageno`, `safesearch` 0-2 |
| Keenable CLI | `source $HOME/.cargo/env && keenable search "query" --published-after 2d` - date filters: `2d`, `7d`, `3mo`, `1y`; `--site <domain>`; YAML output |
| Plain HTTP | `curl -s "http://localhost:3005/search?q=QUERY&format=json"` - self-hosted SearXNG JSON |

## Page extraction

| Capability | Clients |
|---|---|
| Built-in extract tool | `web_extract(urls=[...], char_limit=N)` - markdown out; over-budget pages head+tail truncated, full text saved to disk |
| SearXNG via mcpc | `mcpc @searxng tools-call web_url_read url:="..." section:="Auth" paragraphRange:="1-10" readHeadings:=true` |
| Keenable CLI | `keenable fetch https://example.com/article` - clean markdown |
| Browser (JS-heavy, login-walled) | Playwright-family browser tool; navigate, wait, read DOM text |

## Blocked-page recovery ladder

When a fetch 403s, 429s, hits a paywall or a bot wall, cheapest first:

1. Wayback Machine availability API, then the snapshot
2. archive.today mirrors: `archive.ph`, `.md`, `.li`, `.is`
3. Server-side render reader (e.g. Jina `r.jina.ai/<url>`) when a key exists
4. API pivot on the same host: `/api/`, `/graphql`, `.json`, RSS
5. Real browser as the last, most expensive route

Cite every recovered copy with its provenance: snapshots carry their archive
date and never stand in for live data on freshness-sensitive questions.

## Freshness

1. Prefer a time-filtered search for news, releases, prices: `time_range` (SearXNG), `--published-after` (Keenable), year terms in the query (built-in).
2. Confirm version numbers on the vendor's own host (`site:` filter) before asserting them.
3. Record the access date per source for the report's source table.
