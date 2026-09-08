---
name: go-browser-tests
description: 'Go browser testing with chromedp for HTMX applications, real browser automation. Use when testing HTMX frontend interactions, authentication flows, or any scenario requiring a real browser. Runs in test/e2e/browser/ with chromedp. Keywords: browser testing, chromedp, e2e browser, HTMX testing, frontend automation, real browser test.'
license: MIT
metadata:
  audience: developers
  workflow: testing
  category: browser-testing
  technologies: go, chromedp, htmx
---

## What I do

Browser testing with chromedp for HTMX applications.

## When to use me

- Testing HTMX applications
- Testing frontend interactions
- Testing authentication flows

## Rules

### Location
- **Directory**: `test/e2e/browser/`
- **Package**: `package browser_test`
- **Build Tags**: DO NOT USE

### Test Structure

```go
func TestFrontend_Login(t *testing.T) {
    if testing.Short() {
        t.Skip("Skipping browser tests in short mode")
    }
    
    // given
    ctx, cancel := chromedp.NewContext(context.Background())
    defer cancel()
    
    var title string
    
    // when
    err := chromedp.Run(ctx,
        chromedp.Navigate(appURL+"/login"),
        chromedp.WaitVisible("#email"),
        chromedp.SendKeys("#email", "test@example.com"),
        chromedp.SendKeys("#password", "password"),
        chromedp.Click("#login-button"),
        chromedp.WaitVisible("#dashboard"),
        chromedp.Text("h1", &title),
    )
    
    // then
    require.NoError(t, err)
    assert.Equal(t, "Dashboard", title)
}
```

### HTMX Lifecycle Testing

```go
func WaitForHTMXComplete(selector string) chromedp.Action {
    return chromedp.Poll(`(selector) => {
        const el = document.querySelector(selector);
        return el && !el.classList.contains('htmx-request');
    }`, selector)
}

// Usage
chromedp.SendKeys("#search", "query"),
chromedp.WaitVisible(".htmx-request"),
WaitForHTMXComplete("#results"),
```

### Login Helper

```go
func loginToDashboard(ctx context.Context, email, password, appURL string) chromedp.Tasks {
    return chromedp.Tasks{
        chromedp.Navigate(appURL+"/login"),
        chromedp.WaitVisible("#email"),
        chromedp.SendKeys("#email", email),
        chromedp.SendKeys("#password", password),
        chromedp.Click("#login-button"),
        chromedp.WaitVisible("#dashboard"),
    }
}
```

## Requirements

1. **Request Lifecycle**: Wait for `.htmx-request` to disappear
2. **Authentication**: Test JWT cookies in real browser
3. **UI Interaction**: Use `data-testid` attributes

## Commands

```bash
<runner> test-browser
<runner> test-e2e-up    # Start services first

# Use project's runner: make or just
```

## Important

- Browser tests are the ONLY tests that validate real user experience
- HTTP tests DO NOT validate frontend functionality

## Forbidden

- NEVER skip browser tests for frontend features
- NEVER use HTTP tests for HTMX behavior
- NEVER use build tags
