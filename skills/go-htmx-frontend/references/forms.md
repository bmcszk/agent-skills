# Forms & Validation
## Forms and Validation

From official docs: https://templ.guide/syntax-and-usage/forms/

### View Model Pattern

```go
// model.go
type Model struct {
    Initial          bool
    Name             string
    Email            string
    Error            string
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

### Form Template

```go
// form.templ
package forms

templ View(m Model) {
    <h1>Add Contact</h1>
    <form id="form" method="post" hx-boost="true">
        @CSRF()
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

### Form Handler with gorilla/schema

```go
// handler.go
import "github.com/gorilla/schema"

func (h *Handler) Post(w http.ResponseWriter, r *http.Request) {
    // Parse form
    err := r.ParseForm()
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    
    var model Model
    dec := schema.NewDecoder()
    dec.IgnoreUnknownKeys(true)
    err = dec.Decode(&model, r.PostForm)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    
    // Validate
    if len(model.Validate()) > 0 {
        h.DisplayForm(w, r, model)
        return
    }
    
    // Save and redirect
    http.Redirect(w, r, "/contacts", http.StatusSeeOther)
}
```

### CSRF Protection

```go
// main.go
import "github.com/gorilla/csrf"

func main() {
    csrfMiddleware := csrf.Protect(
        []byte("32-byte-secret-key-here-1234567890"),
        csrf.Secure(true),
    )
    http.ListenAndServe(":8080", csrfMiddleware(router))
}
```

```go
// csrf.templ
templ CSRF() {
    <input 
        type="hidden" 
        name="_csrf" 
        value={ ctx.Value("gorilla.csrf.Token").(string) }
    />
}
```

---

