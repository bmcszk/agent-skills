---
name: interactive-browser-testing
description: >-
  Use when driving interactive real-time browser tests with Playwright and MiniMax via mcpc.
metadata:
  audience: developers
  workflow: interactive-testing
  category: manual-testing
  technologies: mcpc, playwright, minimax, browser-automation
---

## Setup

```bash
mcpc connect <your mcpc config>:playwright @pw
mcpc connect <your mcpc config>:MiniMax @minimax
```

## Critical Rules

1. **BROWSER ONLY** - Never use curl/fetch/http clients
2. **SCREENSHOTS REQUIRED** - Every step must have visual proof
3. **SNAPSHOT FIRST** - Understand page before interacting
4. **AI ANALYSIS** - Use MiniMax via mcpc to analyze screenshots
5. **ISSUES TO TRACKER** - Log all issues found (check duplicates first)

## Screenshot Storage

```
test-results/
├── screenshots/YYYY-MM-DD/   # Daily folders
└── reports/                   # Test reports
```

This directory should be in `.gitignore`.

Full command tables: read `references/tools.md` when invoking browser or image-analysis tools.

## Testing Workflow

### 1. Setup
```bash
mkdir -p test-results/screenshots/$(date +%Y-%m-%d)
mkdir -p test-results/reports
```

### 2. Verify App Running
```bash
1. mcpc @pw tools-call browser_navigate url:=<app-URL>
2. mcpc @pw tools-call browser_take_screenshot
3. mcpc @minimax tools-call understand_image prompt:="Describe the page" image_source:=<screenshot-path>
4. If fails, check logs and restart
```

### 3. Execute Tests
```
For each step:
1. mcpc @pw tools-call browser_snapshot (understand current state)
2. mcpc @pw tools-call browser_click/browser_type (perform action)
3. mcpc @pw tools-call browser_wait_for text:=<expected>
4. mcpc @pw tools-call browser_take_screenshot (save to test-results/)
5. mcpc @minimax tools-call understand_image prompt:="Analyze..." image_source:=<screenshot>
6. mcpc @pw tools-call browser_console_messages (check errors)
7. If issue: check tracker for duplicates, then create
```

## AI Analysis Prompts

**Forms:**
```
"Analyze this form: 1) All fields visible 2) Labels correct 3) Validation state 4) Submit button state 5) Layout issues"
```

**Errors:**
```
"Analyze this error: 1) Error message 2) Error type 3) User impact 4) Suggested fix"
```

**Dashboards:**
```
"Analyze this dashboard: 1) All widgets loaded 2) Data correct 3) Charts rendered 4) No broken images"
```

## Screenshot Naming

- `01-description.png` - Numbered steps
- `ERROR-xx-description.png` - Error states
- Save to: `test-results/screenshots/YYYY-MM-DD/`

## Forbidden

- curl, fetch, http clients
- Testing without screenshots
- Skipping snapshot step
- Skipping AI analysis
- Creating duplicate issues

## Report Format

```markdown
## Test Report: [Feature]

**Date:** YYYY-MM-DD
**Screenshots:** test-results/screenshots/YYYY-MM-DD/

### Summary
- Status: PASS / FAIL
- Steps: X/Y passed
- Issues: [count]

### Steps
| # | Step | Status | Screenshot | Analysis |
|---|------|--------|------------|----------|
| 1 | Navigate | PASS | 01-nav.png | Page loaded |

### Issues
| Issue | Severity | Evidence | Tracker ID |
|-------|----------|----------|------------|

### Console Errors
[From mcpc @pw tools-call browser_console_messages]

### Recommendations
[What to fix]
```
