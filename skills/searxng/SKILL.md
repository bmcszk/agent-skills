---
name: searxng
description: 'Privacy-focused web search and URL content reading via SearXNG (mcpc). Use when you need meta-search across Google/Bing/DuckDuckGo without tracking, or to fetch and extract content from any URL with heading/paragraph filtering. Tools: searxng_web_search for private search, web_url_read for content extraction. Keywords: searxng, private search, meta search, privacy search, url content extraction, read article, web fetch.'
license: MIT
metadata:
  audience: developers
  workflow: research
  category: search
  technologies: mcpc, searxng, web-search, content-extraction
---

## What this does

Provides two complementary capabilities:

1. **Web search** — Privacy-focused meta-search via SearXNG (aggregates Google, Bing, DuckDuckGo, etc.)
2. **URL content reading** — Fetch and extract content from any URL with heading/paragraph/section filtering

## Setup

```bash
mcpc connect ~/.mcpc/mcp.json:searxng @searxng
```

## Tools

### `searxng_web_search`

Search the web using the SearXNG meta-search engine.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search query |
| `pageno` | number | no | Page number, starts at 1 (default: 1) |
| `time_range` | enum | no | Filter by time: `day`, `month`, `year` |
| `language` | string | no | Language code (e.g., `en`, `fr`, `de`). Default: `all` |
| `safesearch` | enum | no | Filter level: 0=None, 1=Moderate, 2=Strict (default: 0) |

**Example:**
```bash
mcpc @searxng tools-call searxng_web_search query:="Go generics best practices 2025" time_range:="month" language:="en"
```

### `web_url_read`

Read and extract content from a URL. Supports heading-based section extraction and paragraph filtering.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | yes | URL to read |
| `startChar` | number | no | Starting character position (default: 0) |
| `maxLength` | number | no | Max characters to return |
| `section` | string | no | Extract content under a specific heading |
| `paragraphRange` | string | no | Paragraph ranges: `1-5`, `3`, `10-` |
| `readHeadings` | boolean | no | Return only headings instead of full content |

**Examples:**
```bash
mcpc @searxng tools-call web_url_read url:="https://go.dev/blog/go1.24" readHeadings:=true
mcpc @searxng tools-call web_url_read url:="https://docs.example.com/api" section:="Authentication"
mcpc @searxng tools-call web_url_read url:="https://example.com/long-article" paragraphRange:="1-10"
```

## Workflow

### Research a topic

```bash
1. mcpc @searxng tools-call searxng_web_search query:="topic keywords" → find relevant URLs
2. mcpc @searxng tools-call web_url_read url:=<result_link> → read full content
3. mcpc @searxng tools-call web_url_read url:=<link> section:="Specific Section" → read specific part
```

### Check recent news

```bash
1. mcpc @searxng tools-call searxng_web_search query:="Kubernetes release" time_range:="month"
2. mcpc @searxng tools-call web_url_read url:=<result_link> readHeadings:=true → scan structure
3. mcpc @searxng tools-call web_url_read url:=<link> section:="What's New" → read relevant section
```

### Read documentation

```bash
1. mcpc @searxng tools-call searxng_web_search query:="library name docs" → find official docs
2. mcpc @searxng tools-call web_url_read url:=<docs_url> readHeadings:=true → get table of contents
3. mcpc @searxng tools-call web_url_read url:=<docs_url> section:="Getting Started" → read specific section
```

## Best practices

- Use `time_range` for recent results: `day` for breaking news, `month` for recent updates
- Use `readHeadings:=true` first to scan a page structure before reading content
- Use `section` parameter to extract only relevant sections from long pages
- Use `paragraphRange` to paginate through very long articles
- Combine with `maxLength` to avoid token overload from large pages
- For non-English content, set `language` parameter for better results
