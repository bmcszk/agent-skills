# Templ

Docs: https://templ.guide/ and https://templ.guide/syntax-and-usage/template-composition/

## Install

```bash
# Templ CLI (Go 1.24+), as a project tool
go get -tool github.com/a-h/templ/cmd/templ@latest

# Or as a global binary
go install github.com/a-h/templ/cmd/templ@latest

# Runtime dependency
go get github.com/a-h/templ
```

Run `templ generate` before `go build`. Generated `*_templ.go` files are build output. Keep them out of version control unless the project already commits them.

## Basic component

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

## Layout with children

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

Use the layout:

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

## Components as parameters

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

## Conditional classes with templ.KV

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

## Loops

```go
templ UserList(users []User) {
    <ul>
        for _, user := range users {
            <li>{ user.Name } - { user.Email }</li>
        }
    </ul>
}
```

## Conditionals

```go
templ Status(isActive bool) {
    if isActive {
        <span class="text-green-500">Active</span>
    } else {
        <span class="text-red-500">Inactive</span>
    }
}
```
