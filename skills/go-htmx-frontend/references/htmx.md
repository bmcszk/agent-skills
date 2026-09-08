# HTMX
## HTMX Integration

### HTMX Form with Partial Update

From official docs: https://templ.guide/server-side-rendering/htmx/

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
- `hx-post="/"` - POST to this endpoint
- `hx-select="#countsForm"` - Extract this element from response
- `hx-swap="outerHTML"` - Replace the form element

### HTMX Patterns

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

### HTMX Loading States CSS

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

### hx-on Attributes (JavaScript Events)

From official docs - for inline JavaScript:

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

---

