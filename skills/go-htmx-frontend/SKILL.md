---
name: go-htmx-frontend
description: 'Server-side frontend development with Go, HTMX, and Templ - type-safe, minimal JavaScript. Use when building web UIs with Go using Templ components, HTMX 2.x for interactivity, Tailwind CSS v4, or Alpine.js. Covers installation, syntax, HTMX integration, forms, handlers, streaming, testing, and deployment. Keywords: htmx, templ, go frontend, server-side rendering, tailwind css, alpine js, web development.'
license: MIT
metadata:
  audience: developers
  workflow: development
  category: frontend
  technologies: go, htmx, templ, tailwind, alpinejs
---

## What I Do

Build web UIs with Go using:
- **Templ**: Type-safe HTML components
- **HTMX 2.x**: Hypermedia-driven interactivity
- **Tailwind CSS v4**: CSS-first styling
- **Alpine.js**: Client state (when needed)

## Official Documentation

**ALWAYS check these sources:**
- https://templ.guide/ - Full Templ documentation
- https://templ.guide/server-side-rendering/htmx/ - HTMX integration
- https://templ.guide/syntax-and-usage/template-composition/ - Component composition
- https://templ.guide/syntax-and-usage/forms/ - Forms and validation
- https://htmx.org/docs/ - HTMX reference
- https://htmx.org/examples/ - HTMX examples
- https://tailwindcss.com/blog/tailwindcss-v4 - Tailwind v4 documentation

---

## Installation

### Templ

```bash
# Templ CLI (Go 1.24+)
go install github.com/a-h/templ/cmd/templ@latest

# Or as project tool
go get -tool github.com/a-h/templ/cmd/templ@latest

# Go dependencies
go get github.com/a-h/templ
```

### Tailwind CSS v4 (Standalone CLI - No Node.js Required)

**IMPORTANT: Use the standalone CLI for Go projects. Do NOT use npm/Node.js.**

```bash
# Download standalone CLI (Linux/macOS)
curl -sL https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-$(uname -m)-unknown-linux-gnu -o tailwindcss
chmod +x tailwindcss
sudo mv tailwindcss /usr/local/bin/

# Or install to project tools directory
mkdir -p tools
curl -sL https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-$(uname -m)-unknown-linux-gnu -o tools/tailwindcss
chmod +x tools/tailwindcss
```

**Why Standalone CLI over npm:**
- No `node_modules` folder
- No `package.json` / `package-lock.json`
- Single binary download
- Cleaner project structure
- Faster builds (v4 is 5x faster)
- No dependency management overhead

### HTMX

```bash
# Download HTMX 2.x to static folder
mkdir -p static/js
curl -sL https://unpkg.com/htmx.org@2/dist/htmx.min.js -o static/js/htmx.min.js
```

### Alpine.js (Optional - for client state)

```bash
curl -sL https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js -o static/js/alpine.min.js
```

---


## References

Specialized topics are split into focused reference files:

- [Templ](references/templ.md) — Type-safe HTML components, composition, loops, conditionals
- [HTMX](references/htmx.md) — Form partials, patterns, loading states, hx-on events
- [Tailwind CSS v4](references/tailwind.md) — Standalone CLI, @source directives, build commands
- [Forms & Validation](references/forms.md) — View models, form templates, CSRF protection
- [Deployment & Build](references/deployment.md) — justfile, CI, build commands, production config

## HTTP Handlers

### Static Pages with templ.Handler

```go
// main.go
package main

import (
    "net/http"
    "github.com/a-h/templ"
)

func main() {
    http.Handle("/", templ.Handler(HomePage()))
    http.Handle("/404", templ.Handler(NotFound(), templ.WithStatus(http.StatusNotFound)))
    http.ListenAndServe(":8080", nil)
}
```

### Dynamic Data with Render

```go
// handler.go
package main

import (
    "net/http"
    "time"
)

type NowHandler struct {
    Now func() time.Time
}

func (nh NowHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // Use Render for dynamic data
    ShowTime(nh.Now()).Render(r.Context(), w)
}

func main() {
    http.Handle("/", NowHandler{Now: time.Now})
    http.ListenAndServe(":8080", nil)
}
```

### HTMX-Aware Handler

```go
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    
    user, err := h.service.GetUser(r.Context(), id)
    if err != nil {
        w.WriteHeader(http.StatusNotFound)
        NotFound().Render(r.Context(), w)
        return
    }
    
    // Check if HTMX request
    if r.Header.Get("HX-Request") == "true" {
        // Return partial only
        UserRow(user).Render(r.Context(), w)
    } else {
        // Return full page
        UserPage(user).Render(r.Context(), w)
    }
}
```

---

## Context for Prop Drilling

From official docs: https://templ.guide/syntax-and-usage/context/

### Type-Safe Context Access

```go
// context.go
type contextKey string

var themeContextKey contextKey = "theme"

func GetTheme(ctx context.Context) string {
    if theme, ok := ctx.Value(themeContextKey).(string); ok {
        return theme
    }
    return ""
}
```

```go
// component.templ
templ ThemeDisplay() {
    <div>{ GetTheme(ctx) }</div>
}
```

### HTTP Middleware for Context

```go
func ThemeMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        ctx := context.WithValue(r.Context(), themeContextKey, "dark")
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

---

## HTTP Streaming

From official docs: https://templ.guide/server-side-rendering/streaming/

### Enable Streaming

```go
templ.Handler(component, templ.WithStreaming()).ServeHTTP(w, r)
```

### Streaming with Flush

```go
templ StreamingPage(data chan string) {
    <!DOCTYPE html>
    <html>
        <head><title>Streaming</title></head>
        <body>
            <h1>Streaming Page</h1>
            for d := range data {
                @templ.Flush() {
                    <div>{ d }</div>
                }
            }
        </body>
    </html>
}
```

### Suspense Pattern with Shadow DOM

```go
templ Slot(name string) {
    <slot name={ name }>
        <div>Loading { name }...</div>
    </slot>
}

templ SuspensePage(data chan SlotContents) {
    <!DOCTYPE html>
    <html>
        <head><title>Suspense</title></head>
        <body>
            @templ.Flush() {
                <template shadowrootmode="open">
                    @Slot("a")
                    @Slot("b")
                </template>
            }
            for sc := range data {
                @templ.Flush() {
                    <div slot={ sc.Name }>
                        @sc.Contents
                    </div>
                }
            }
        </body>
    </html>
}
```

---

## Testing

### Component Test

```go
func TestHello(t *testing.T) {
    var buf bytes.Buffer
    err := Hello("World").Render(context.Background(), &buf)
    
    require.NoError(t, err)
    assert.Contains(t, buf.String(), "Hello, World!")
}
```

### Handler Test with HTMX

```go
func TestHandler(t *testing.T) {
    req := httptest.NewRequest("GET", "/users", nil)
    req.Header.Set("HX-Request", "true")
    
    rr := httptest.NewRecorder()
    handler.ServeHTTP(rr, req)
    
    assert.Equal(t, http.StatusOK, rr.Code)
}
```

---

## Key Principles

1. **Server-First**: Render HTML server-side
2. **Type Safety**: Templ validates at compile time
3. **Minimal JS**: Alpine.js only for client state
4. **Progressive Enhancement**: Works without JS
5. **No Node.js**: Use Tailwind standalone CLI, not npm
6. **CSS-First Config**: Tailwind v4 uses `@theme` in CSS, no JS config
7. **Check Docs**: Always verify with official documentation

## Resources

- [Templ Docs](https://templ.guide/)
- [Templ + HTMX Guide](https://templ.guide/server-side-rendering/htmx/)
- [Templ Forms Guide](https://templ.guide/syntax-and-usage/forms/)
- [HTMX Docs](https://htmx.org/)
- [HTMX Examples](https://htmx.org/examples/)
- [Tailwind CSS v4](https://tailwindcss.com/blog/tailwindcss-v4)
- [Tailwind Standalone CLI](https://tailwindcss.com/blog/standalone-cli)
- [templUI](https://templui.io/) - Component library
