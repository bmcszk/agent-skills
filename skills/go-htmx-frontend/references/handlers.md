# HTTP handlers

Use this when a handler renders a component, when one route serves a full page and an HTMX partial, when you need request-scoped context in components, or when you stream.

## Static pages with templ.Handler

```go
// main.go
package main

import (
    "log"
    "net/http"

    "github.com/a-h/templ"
)

func main() {
    http.Handle("/", templ.Handler(HomePage()))
    http.Handle("/404", templ.Handler(NotFound(), templ.WithStatus(http.StatusNotFound)))
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

## Dynamic data with Render

`Render` returns an error. Check it. Once the handler has written part of the body, the status code is gone, so log the error and stop.

```go
// handler.go
package main

import (
    "log"
    "net/http"
    "time"
)

type NowHandler struct {
    Now func() time.Time
}

func (nh NowHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    if err := ShowTime(nh.Now()).Render(r.Context(), w); err != nil {
        log.Printf("render: %v", err)
    }
}

func main() {
    http.Handle("/", NowHandler{Now: time.Now})
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

## HTMX-aware handler

One route serves a full page to a browser navigation and a partial to an HTMX request.

- Treat a request as a partial request only when `HX-Request` is `true` and `HX-Boosted` is not `true`. A boosted link (`hx-boost`) sends `HX-Request: true` but swaps the whole `<body>`, so it needs the full page.
- Set `Vary: HX-Request` before the first write. Without it a cache can serve the partial to a browser navigation to the same URL.
- Map a not-found error to `404`. Log every other error and return a generic `500`. Do not write `err.Error()` to the response.
- HTMX 2 does not swap 4xx or 5xx responses by default. See [htmx.md](htmx.md#error-responses).

```go
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    w.Header().Add("Vary", "HX-Request")

    user, err := h.service.GetUser(r.Context(), r.PathValue("id"))
    if errors.Is(err, service.ErrNotFound) {
        w.WriteHeader(http.StatusNotFound)
        h.render(w, r, NotFound())
        return
    }
    if err != nil {
        h.logger.ErrorContext(r.Context(), "get user", "error", err)
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }

    view := UserPage(user)
    if isPartialRequest(r) {
        view = UserRow(user)
    }
    h.render(w, r, view)
}

func isPartialRequest(r *http.Request) bool {
    return r.Header.Get("HX-Request") == "true" && r.Header.Get("HX-Boosted") != "true"
}

func (h *Handler) render(w http.ResponseWriter, r *http.Request, c templ.Component) {
    if err := c.Render(r.Context(), w); err != nil {
        h.logger.ErrorContext(r.Context(), "render", "error", err)
    }
}
```

## Context for request-scoped values

Docs: https://templ.guide/syntax-and-usage/context/

Context fits values that many components read and that are not security input, such as a theme. Pass everything else (CSRF token, the user for one page) as a component parameter. A parameter is checked at compile time. A context lookup is not.

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

```go
func ThemeMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        ctx := context.WithValue(r.Context(), themeContextKey, "dark")
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

## Streaming

Docs: https://templ.guide/server-side-rendering/streaming/

Enable streaming on the handler:

```go
templ.Handler(component, templ.WithStreaming()).ServeHTTP(w, r)
```

Flush parts of the page as data arrives:

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

Suspense with Shadow DOM shows placeholders first and fills the slots as data arrives:

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

A streamed response can no longer change its status after the first flush. Run validation and lookups before the first flush.
