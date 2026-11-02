# HTMX

Docs: https://htmx.org/docs/ and https://templ.guide/server-side-rendering/htmx/

## Install

```bash
# HTMX 2.x
mkdir -p static/js
curl -sL https://unpkg.com/htmx.org@2/dist/htmx.min.js -o static/js/htmx.min.js

# Alpine.js, only when a page needs client state
curl -sL https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js -o static/js/alpine.min.js
```

Commit the downloaded file so the build does not depend on a CDN.

## Form with a partial update

```go
// counts.templ
package components

import "strconv"

templ Counts(global, session int) {
    <form
        id="countsForm"
        action="/"
        method="POST"
        hx-post="/"
        hx-select="#countsForm"
        hx-swap="outerHTML"
    >
        <div class="columns">
            <div class="column">
                <h1>{ strconv.Itoa(global) }</h1>
                <p>Global</p>
                <button type="submit" name="global" value="global">+1</button>
            </div>
            <div class="column">
                <h1>{ strconv.Itoa(session) }</h1>
                <p>Session</p>
                <button type="submit" name="session" value="session">+1</button>
            </div>
        </div>
    </form>
}
```

Key attributes:
- `hx-post="/"` posts to this endpoint.
- `hx-select="#countsForm"` extracts this element from the response.
- `hx-swap="outerHTML"` replaces the form element.

## Patterns

```go
// Click to load
templ LoadButton() {
    <button hx-get="/users" hx-target="#user-list">Load Users</button>
    <div id="user-list"></div>
}

// Real-time search with debounce
templ SearchInput() {
    <input
        type="search"
        name="q"
        hx-get="/search"
        hx-trigger="keyup changed delay:300ms"
        hx-target="#results"
    />
    <div id="results"></div>
}

// Infinite scroll
templ InfiniteScroll() {
    <div
        hx-get="/more-items"
        hx-trigger="revealed"
        hx-swap="beforeend"
    >
        Loading...
    </div>
}

// Loading indicator
templ SubmitButton() {
    <button hx-post="/action" hx-indicator="#spinner">
        Submit
    </button>
    <span id="spinner" class="htmx-indicator">Loading...</span>
}
```

## Loading-state CSS

```css
.htmx-indicator {
    display: none;
}
.htmx-request .htmx-indicator {
    display: inline;
}
.htmx-request.htmx-indicator {
    display: inline;
}
```

## Error responses

HTMX 2 does not swap 4xx and 5xx responses by default. The default `htmx.config.responseHandling` marks them as errors with `swap: false`. A handler that returns `404` or `422` with an HTML fragment shows nothing on the page.

Pick one:
- Return `200` with the fragment when the fragment is an inline validation message.
- Opt in to swapping specific codes, for example 422 for validation errors:

```html
<script>
  htmx.config.responseHandling = [
    {code: "204", swap: false},
    {code: "[23]..", swap: true},
    {code: "422", swap: true, error: false},
    {code: "[45]..", swap: false, error: true},
  ];
</script>
```

Put that block after the HTMX script. HTMX takes the first rule that matches, so keep `422` before `[45]..`.

Handler side of full pages and partials: [handlers.md](handlers.md).

## hx-on attributes

For inline JavaScript events:

```go
// Static JavaScript
templ ClickAlert() {
    <button hx-on:click="alert('Hello')">Click me</button>
}

// Dynamic JavaScript with server data
templ DynamicAlert(message string) {
    <script>
        function showMessage(msg) {
            alert(msg);
        }
    </script>
    <button hx-on:click={ templ.JSFuncCall("showMessage", message) }>
        Click me
    </button>
}
```
