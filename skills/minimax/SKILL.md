---
name: minimax
description: 'AI-powered web search and image understanding via MiniMax (mcpc). Use when you need real-time web search (Google-like) or to analyze/describe/extract information from images (local files or URLs). Tools: web_search for current info, understand_image for visual analysis. Keywords: minimax, web search, image understanding, image analysis, visual search, ai search.'
license: MIT
metadata:
  audience: developers
  workflow: research
  category: ai-tools
  technologies: mcpc, minimax, web-search, image-analysis
---

## What this does

Provides two AI-powered capabilities:

1. **Web search** — Google-like search for real-time or external information
2. **Image understanding** — Analyze, describe, or extract information from images (local files or URLs)

## Setup

```bash
mcpc connect ~/.mcpc/mcp.json:MiniMax @minimax
```

## Tools

### `web_search`

Search the web for real-time information. Works like Google Search.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search query — aim for 3-5 keywords. For time-sensitive topics, include the date. |

**Returns:** JSON with `organic` results (title, link, snippet, date) and `related_searches`.

**Example:**
```bash
mcpc @minimax tools-call web_search query:="Go 1.24 generics improvements 2025"
```

**Response structure:**
```json
{
  "organic": [
    { "title": "...", "link": "https://...", "snippet": "...", "date": "..." }
  ],
  "related_searches": [{ "query": "..." }]
}
```

### `understand_image`

Analyze and interpret image content from local files or URLs.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | yes | What to analyze or extract from the image |
| `image_source` | string | yes | File path (relative or absolute) or HTTP/HTTPS URL |

**Supported formats:** JPEG, PNG, WebP only.

**Examples:**
```bash
mcpc @minimax tools-call understand_image prompt:="Describe the UI layout and any issues" image_source:="/screenshots/page.png"
mcpc @minimax tools-call understand_image prompt:="Extract text from this screenshot" image_source:="https://example.com/image.jpg"
```

**Important:** Strip any `@` prefix from file paths before passing as `image_source`.

## When to use

- Need real-time information not in training data
- User asks about current events, recent releases, or time-sensitive topics
- Analyzing screenshots, UI mockups, diagrams, or photos
- Extracting text or data from images
- Verifying facts with current web sources

## Workflow

### Research a topic

```bash
1. mcpc @minimax tools-call web_search query:="topic keywords"
2. Review organic results for relevant links
3. Optionally use mcpc @searxng tools-call web_url_read to fetch full page content
```

### Analyze a screenshot

```bash
1. Take or receive a screenshot (e.g., via mcpc @pw tools-call browser_take_screenshot)
2. mcpc @minimax tools-call understand_image prompt:="Analyze this: 1) UI layout 2) Errors visible 3) Suggestions" image_source:=<path>
3. Use analysis to inform next steps
```

## Best practices

- **Search queries:** Use 3-5 specific keywords. Include dates for time-sensitive queries.
- **Image prompts:** Be specific about what to analyze — list numbered points for structured output.
- **Rephrasing:** If search returns no useful results, rephrase with different keywords.
- **File paths:** Always strip `@` prefix from paths before passing as `image_source`.
