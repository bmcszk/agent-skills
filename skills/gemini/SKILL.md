---
name: gemini
description: 'Google Gemini AI assistant for code analysis, brainstorming, file analysis, and general questions via Gemini (mcpc). Use when you need a second opinion on code, architectural review, brainstorming ideas, or analyzing files. Supports multiple brainstorming methodologies and structured change mode for code edits. Keywords: gemini, google ai, code analysis, brainstorming, code review, second opinion, ask gemini.'
license: MIT
metadata:
  audience: developers
  workflow: assistant
  category: ai-tools
  technologies: mcpc, gemini, google-ai, brainstorming
---

## What this does

Provides access to Google Gemini AI models for code analysis, brainstorming, file analysis, and general questions. Supports multiple brainstorming methodologies and structured change mode for code edits.

## Setup

```bash
mcpc connect ~/.mcpc/mcp.json:gemini-cli @gemini
```

## Tools

### `ask-gemini`

Ask Gemini a question or request analysis. Supports file references via `@` syntax.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | yes | Analysis request. Use `@filename` to include files. |
| `model` | string | no | Model to use (default: `gemini-2.5-pro`). E.g., `gemini-2.5-flash`. |
| `sandbox` | boolean | no | Run in isolated sandbox for risky operations (default: false) |
| `changeMode` | boolean | no | Return structured edit suggestions (default: false) |

**Examples:**
```bash
mcpc @gemini tools-call ask-gemini prompt:="@main.go explain the architecture and suggest improvements"
mcpc @gemini tools-call ask-gemini prompt:="Compare REST vs GraphQL for a blog API" model:="gemini-2.5-flash"
mcpc @gemini tools-call ask-gemini prompt:="@config.yaml refactor to use environment variables" changeMode:=true
```

### `brainstorm`

Generate ideas using creative frameworks with domain context and analysis.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | yes | Challenge or question to explore |
| `methodology` | enum | no | `divergent`, `convergent`, `scamper`, `design-thinking`, `lateral`, `auto` (default) |
| `domain` | string | no | Context: `software`, `business`, `creative`, `research`, `product`, `marketing` |
| `constraints` | string | no | Limitations (budget, time, technical, legal) |
| `existingContext` | string | no | Background info or previous attempts |
| `ideaCount` | integer | no | Target number of ideas (default: 12) |
| `includeAnalysis` | boolean | no | Include feasibility/impact analysis (default: true) |
| `model` | string | no | Model override |

**Examples:**
```bash
mcpc @gemini tools-call brainstorm prompt:="API design for multiplayer game" domain:="software" methodology:="design-thinking"
mcpc @gemini tools-call brainstorm prompt:="Reduce churn in SaaS" domain:="business" methodology:="scamper" constraints:="low budget"
```

### `fetch-chunk`

Retrieve cached chunks from a `changeMode` response.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cacheKey` | string | yes | Cache key from initial changeMode response |
| `chunkIndex` | number | yes | 1-based chunk index |

### `ping`

Echo test. **Parameters:** `prompt` (optional string).

### `Help`

Show help information. No parameters.

## When to use

- Need a second opinion from a different AI model
- Brainstorming with structured creative frameworks (SCAMPER, Design Thinking, etc.)
- Analyzing files with `@filename` syntax
- Generating structured code change suggestions via `changeMode`
- Quick questions where a different model perspective helps

## Workflow

### Code review with file context

```bash
mcpc @gemini tools-call ask-gemini prompt:="@file.go review for bugs, performance issues, and suggest improvements"
```

### Structured code changes

```bash
1. mcpc @gemini tools-call ask-gemini prompt:="@config.yaml add support for environment variables" changeMode:=true
   # → Returns structured edit with cacheKey if response is chunked
2. mcpc @gemini tools-call fetch-chunk cacheKey:=<key> chunkIndex:=2 → get next chunk if needed
```

### Brainstorming session

```bash
1. mcpc @gemini tools-call brainstorm prompt:="..." domain:="software" methodology:="scamper" ideaCount:=8
2. Review generated ideas with feasibility analysis
3. mcpc @gemini tools-call brainstorm prompt:="Refine top 3 ideas" methodology:="convergent" existingContext:=<previous results>
```

## Best practices

- Use `@filename` syntax to give Gemini file context
- Use `gemini-2.5-flash` for faster, cheaper queries; `gemini-2.5-pro` for complex analysis
- Enable `sandbox:=true` when testing potentially risky code
- For brainstorming, let `methodology:="auto"` unless you need a specific framework
- Use `changeMode:=true` when you want structured, applicable edit suggestions
