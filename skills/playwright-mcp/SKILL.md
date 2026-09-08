---
name: playwright-mcp
description: 'Browser automation and testing via Playwright (mcpc) — navigate, interact, verify, and screenshot web pages. Use for E2E testing, UI verification, web scraping, and browser-based workflows. Tools: browser_navigate, browser_click, browser_type, browser_snapshot, browser_take_screenshot, browser_wait_for, browser_evaluate. Keywords: playwright, browser automation, e2e testing, ui testing, web scraping, screenshot, browser mcp.'
license: MIT
metadata:
  audience: developers
  workflow: testing
  category: browser-automation
  technologies: mcpc, playwright, browser-testing, e2e
---

## What this does

Controls a real browser via Playwright for navigation, interaction, verification, and visual capture. Use for E2E testing, UI verification, web scraping, and browser-based workflows.

## Setup

```bash
mcpc connect ~/.mcpc/mcp.json:playwright @pw
```

## Tools

### Navigation

| Tool | Key params | Description |
|------|-----------|-------------|
| `browser_navigate` | `url: str` | Go to URL |
| `browser_navigate_back` | — | Go back |
| `browser_close` | — | Close browser |
| `browser_resize` | `width: num, height: num` | Resize window |
| `browser_tabs` | `action: enum` | Manage tabs (open, close, select) |

### Interaction

| Tool | Key params | Description |
|------|-----------|-------------|
| `browser_click` | `target: str` | Click element (use ref from snapshot) |
| `browser_type` | `target: str, text: str` | Type text into element |
| `browser_press_key` | `key: str` | Press keyboard key |
| `browser_hover` | `target: str` | Hover over element |
| `browser_drag` | `startTarget: str, endTarget: str` | Drag and drop |
| `browser_select_option` | `target: str, values: [str]` | Select dropdown option |
| `browser_fill_form` | `fields: [obj]` | Fill multiple form fields |
| `browser_file_upload` | `paths?: [str]` | Upload files |
| `browser_handle_dialog` | `accept: bool` | Handle alert/confirm/prompt dialogs |
| `browser_drop` | `target: str` | Drop element |

### Verification

| Tool | Key params | Description |
|------|-----------|-------------|
| `browser_snapshot` | `target?: str` | **Get page accessibility tree (USE FIRST before interacting)** |
| `browser_take_screenshot` | `type?: enum` | **Capture screenshot (REQUIRED for visual proof)** |
| `browser_wait_for` | `time?: num, text?: str` | Wait for condition |
| `browser_console_messages` | `level?: enum` | Get console logs |
| `browser_network_requests` | `filter?: str` | Get network request log |
| `browser_network_request` | `index: int` | Get specific network request details |
| `browser_evaluate` | `function: str` | Run JavaScript in browser |
| `browser_run_code_unsafe` | `code?: str` | Execute arbitrary code (use with caution) |

## Workflow

### Standard testing loop

```bash
1. mcpc @pw tools-call browser_navigate url:="http://localhost:3000"
2. mcpc @pw tools-call browser_snapshot → understand page structure
3. mcpc @pw tools-call browser_click/browser_type → perform action
4. mcpc @pw tools-call browser_wait_for text:="expected result"
5. mcpc @pw tools-call browser_take_screenshot → visual proof
6. mcpc @pw tools-call browser_console_messages → check for errors
```

### Form filling

```bash
1. mcpc @pw tools-call browser_snapshot → identify form fields
2. mcpc @pw tools-call browser_fill_form fields:='[{"target":"email","value":"test@example.com"},{"target":"password","value":"secret123"}]'
3. mcpc @pw tools-call browser_click target:="submit button"
4. mcpc @pw tools-call browser_wait_for text:="Welcome"
5. mcpc @pw tools-call browser_take_screenshot → verify result
```

### Debugging

```bash
1. mcpc @pw tools-call browser_snapshot → get current state
2. mcpc @pw tools-call browser_console_messages level:="error" → check errors
3. mcpc @pw tools-call browser_network_requests filter:="api" → check API calls
4. mcpc @pw tools-call browser_take_screenshot → visual state
```

## Critical rules

1. **SNAPSHOT FIRST** — Always run `mcpc @pw tools-call browser_snapshot` before interacting to understand page structure and get element refs
2. **Use refs** — Elements from snapshot have `ref` attributes; use these as `target` values
3. **Screenshots** — Take screenshots at every significant step for visual evidence
4. **Wait** — Use `mcpc @pw tools-call browser_wait_for` after actions to ensure page has updated
5. **Check console** — Run `mcpc @pw tools-call browser_console_messages` to catch JavaScript errors

## Best practices

- Start every session with `mcpc @pw tools-call browser_navigate` to set the initial URL
- Use `mcpc @pw tools-call browser_snapshot` to discover element selectors — don't guess CSS selectors
- Chain actions: snapshot → interact → wait → screenshot → verify
- Close browser with `mcpc @pw tools-call browser_close` when done to free resources
- Use `mcpc @pw tools-call browser_evaluate` sparingly — prefer native tool interactions
