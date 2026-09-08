# Templ
## Templ Syntax

### Basic Component

```go
// components.templ
package components

import "time"

templ Hello(name string) {
    <div>Hello, { name }!</div>
}

templ ShowTime(t time.Time) {
    <div>{ t.String() }</div>
}
```

### Template Composition with Children

```go
// layout.templ
package components

templ Layout(title string) {
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{ title }</title>
        <script src="/static/js/htmx.min.js"></script>
        <link rel="stylesheet" href="/static/css/output.css"/>
    </head>
    <body>
        { children... }
    </body>
    </html>
}
```

### Using Layout with Children

```go
// page.templ
package pages

import "myapp/components"

templ HomePage() {
    @components.Layout("Home") {
        <h1>Welcome</h1>
        @components.Hello("World")
    }
}
```

### Components as Parameters

```go
// components.templ
package components

templ Layout(content templ.Component) {
    <div id="wrapper">
        @content
    </div>
}

// Usage:
templ Page() {
    @Layout(paragraph("Dynamic content"))
}

templ paragraph(text string) {
    <p>{ text }</p>
}
```

### Conditional Classes with templ.KV

```go
templ FormField(name string, hasError bool, value string) {
    <div class={ "form-group", templ.KV("has-error", hasError) }>
        <label for={ name }>{ name }</label>
        <input 
            type="text" 
            id={ name } 
            name={ name } 
            class="form-control" 
            value={ value }
        />
    </div>
}
```

### For Loops

```go
templ UserList(users []User) {
    <ul>
        for _, user := range users {
            <li>{ user.Name } - { user.Email }</li>
        }
    </ul>
}
```

### If/Else

```go
templ Status(isActive bool) {
    if isActive {
        <span class="text-green-500">Active</span>
    } else {
        <span class="text-red-500">Inactive</span>
    }
}
```

---

