# Forms and validation

Docs: https://templ.guide/syntax-and-usage/forms/

## View model

The model has two kinds of fields: values the user submits, and state the server sets (`Initial`, `Error`, `CSRFToken`). Tag server-state fields `schema:"-"`. Without the tag a client can post `initial=true` and skip validation.

```go
// model.go
type Model struct {
    Name      string `schema:"name"`
    Email     string `schema:"email"`
    Initial   bool   `schema:"-"`
    Error     string `schema:"-"`
    CSRFToken string `schema:"-"`
}

func NewModel() Model {
    return Model{Initial: true}
}

func (m *Model) ValidateName() (msgs []string) {
    if m.Initial {
        return
    }
    if m.Name == "" {
        msgs = append(msgs, "Name is required")
    }
    return msgs
}

func (m *Model) NameHasError() bool {
    return len(m.ValidateName()) > 0
}

func (m *Model) Validate() (msgs []string) {
    if m.Initial {
        return
    }
    msgs = append(msgs, m.ValidateName()...)
    return msgs
}
```

## Form template

The handler puts the CSRF token on the model. The component renders it. The component never reads it from `ctx`.

```go
// form.templ
package forms

templ View(m Model) {
    <h1>Add Contact</h1>
    <form id="form" method="post" action="/contacts" hx-boost="true">
        @CSRF(m.CSRFToken)
        <div id="name-group" class={ "form-group", templ.KV("has-error", m.NameHasError()) }>
            <label for="name">Name</label>
            <input
                type="text"
                id="name"
                name="name"
                class="form-control"
                value={ m.Name }
            />
        </div>
        <div id="validation">
            if m.Error != "" {
                <p class="error">{ m.Error }</p>
            }
            if msgs := m.Validate(); len(msgs) > 0 {
                @ValidationMessages(msgs)
            }
        </div>
        <input type="submit" value="Save"/>
    </form>
}

templ ValidationMessages(msgs []string) {
    if len(msgs) > 0 {
        <div class="invalid-feedback">
            <ul>
                for _, msg := range msgs {
                    <li class="error">{ msg }</li>
                }
            </ul>
        </div>
    }
}
```

## Form handler with gorilla/schema

- Decode errors are the client's mistake, but their text names internal fields and types. Log the error. Return a fixed message.
- A validation failure re-renders the form. HTMX 2 does not swap a 4xx response by default. Return `200` with the form, or configure `422` to swap: [htmx.md](htmx.md#error-responses).

```go
// handler.go
import "github.com/gorilla/schema"

var formDecoder = newFormDecoder()

func newFormDecoder() *schema.Decoder {
    dec := schema.NewDecoder()
    dec.IgnoreUnknownKeys(true)
    return dec
}

func (h *Handler) Post(w http.ResponseWriter, r *http.Request) {
    if err := r.ParseForm(); err != nil {
        h.logger.WarnContext(r.Context(), "parse form", "error", err)
        http.Error(w, "invalid form", http.StatusBadRequest)
        return
    }

    var model Model
    if err := formDecoder.Decode(&model, r.PostForm); err != nil {
        h.logger.WarnContext(r.Context(), "decode form", "error", err)
        http.Error(w, "invalid form", http.StatusBadRequest)
        return
    }

    if len(model.Validate()) > 0 {
        model.CSRFToken = csrf.Token(r)
        h.render(w, r, forms.View(model))
        return
    }

    http.Redirect(w, r, "/contacts", http.StatusSeeOther)
}
```

The `GET` handler that shows the empty form sets `model.CSRFToken = csrf.Token(r)` too. `h.render` is in [handlers.md](handlers.md#htmx-aware-handler).

## CSRF protection

There are two options. Pick one per project.

### Option 1: net/http CrossOriginProtection (Go 1.25+)

The standard library rejects non-safe cross-origin browser requests. It checks the `Sec-Fetch-Site` header, or compares the `Origin` host with the `Host`. It needs no key, no cookie, and no token in the form. Requests with neither header (non-browser clients) pass. GET, HEAD, and OPTIONS always pass, so never change state in them.

```go
cop := http.NewCrossOriginProtection()
if err := cop.AddTrustedOrigin("https://admin.example.com"); err != nil {
    log.Fatal(err)
}
log.Fatal(http.ListenAndServe(":8080", cop.Handler(router)))
```

Check the API with `go doc net/http.CrossOriginProtection`. Use this option when every client is a current browser. Use option 2 when you need a token, for example for old browsers.

### Option 2: gorilla/csrf

Load the key from the environment. A key in source is public. The key must be exactly 32 bytes, so store it as 64 hex characters (or base64) and check the length after decoding. `os.Getenv` bytes are not 32 random bytes.

```go
// main.go
import (
    "encoding/hex"

    "github.com/gorilla/csrf"
)

func csrfKey() ([]byte, error) {
    key, err := hex.DecodeString(os.Getenv("CSRF_KEY"))
    if err != nil {
        return nil, fmt.Errorf("decode CSRF_KEY as hex: %w", err)
    }
    if len(key) != 32 {
        return nil, fmt.Errorf("CSRF_KEY must decode to 32 bytes, got %d", len(key))
    }
    return key, nil
}

func main() {
    key, err := csrfKey()
    if err != nil {
        log.Fatal(err)
    }
    protect := csrf.Protect(key, csrf.Secure(true))
    log.Fatal(http.ListenAndServe(":8080", protect(router)))
}
```

Generate a key with `openssl rand -hex 32`. `csrf.Secure(true)` is the default. It sets the cookie as secure, so a plain-HTTP dev server loses the cookie. Use `csrf.Secure(false)` only in local development.

Never write `ctx.Value("gorilla.csrf.Token")` in a component. The string key is an internal detail of the library, the unchecked type assertion panics when the key is missing, and a component rendered with another context loses the token. Read the token in the handler with `csrf.Token(r)` (or `csrf.TemplateField(r)` for a ready hidden input) and pass it to the component.

```go
// csrf.templ
templ CSRF(token string) {
    <input type="hidden" name="gorilla.csrf.Token" value={ token }/>
}
```

`gorilla.csrf.Token` is the default form field name. Change it only with `csrf.FieldName(...)`, and change the template in the same commit.

For `hx-post` requests outside a form, send the token as the `X-CSRF-Token` header. Set it once on `<body>`:

```go
templ Layout(title, csrfToken string) {
    <body hx-headers={ templ.JSONString(map[string]string{"X-CSRF-Token": csrfToken}) }>
        { children... }
    </body>
}
```
