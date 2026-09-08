---
name: context7
description: 'Fetch up-to-date documentation for any library, framework, SDK, API, or CLI tool via Context7 (mcpc). Use when you need current version-accurate docs, code examples, or API references — training data may be outdated. Prefer this over web search for library documentation queries. Keywords: context7, documentation, library docs, API reference, up-to-date docs, version-accurate, code examples.'
license: MIT
metadata:
  audience: developers
  workflow: documentation
  category: reference
  technologies: mcpc, context7, documentation
---

## What this does

Fetches current, version-accurate documentation and code examples for any programming library, framework, SDK, API, CLI tool, or cloud service. Use this even for well-known libraries — training data may not reflect recent changes.

Prefer this over web search for library documentation queries.

## Setup

```bash
mcpc connect ~/.mcpc/mcp.json:context7 @c7
```

## Tools

### `resolve-library-id`

Resolves a package/product name to a Context7-compatible library ID. **MUST call this first** before `query-docs`.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | The question or task — used to rank results by relevance |
| `libraryName` | string | yes | Official library name with proper punctuation (e.g., "Next.js", "Three.js") |

**Returns:** List of matching libraries with IDs (format: `/org/project`), descriptions, snippet counts, reputation scores, and version info.

**Selection:** Pick based on name match, source reputation (High > Medium > Low), snippet coverage, and benchmark score.

### `query-docs`

Retrieves documentation and code examples for a resolved library ID.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `libraryId` | string | yes | Context7 library ID from `resolve-library-id` (e.g., `/vercel/next.js`) |
| `query` | string | yes | Specific question — include relevant details for better results |

## Workflow

```
1. mcpc @c7 tools-call resolve-library-id → get library ID
2. mcpc @c7 tools-call query-docs → get documentation
```

### Examples

```bash
mcpc @c7 tools-call resolve-library-id libraryName:="React" query:="useEffect cleanup function"
# → libraryId: /facebook/react

mcpc @c7 tools-call query-docs libraryId:="/facebook/react" query:="useEffect cleanup function examples"
# → documentation with code examples
```

### With version

```bash
mcpc @c7 tools-call resolve-library-id libraryName:="Next.js" query:="app router"
# → returns versions: /vercel/next.js, /vercel/next.js/v14.3.0-canary.87

mcpc @c7 tools-call query-docs libraryId:="/vercel/next.js/v14.3.0-canary.87" query:="app router setup"
```

## Rules

- Call `resolve-library-id` before `query-docs` (unless user provides `/org/project` format ID)
- Do not call either tool more than **3 times per question**
- Use proper library names: "Next.js" not "nextjs", "Customer.io" not "customerio"
- Write specific queries: "How to set up JWT auth in Express.js" not "auth"
- Never include API keys, passwords, or sensitive data in queries
