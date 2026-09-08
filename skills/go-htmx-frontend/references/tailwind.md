# Tailwind CSS v4
## Tailwind CSS v4 Configuration

**CRITICAL: Tailwind v4 uses CSS-first configuration. No `tailwind.config.js` needed.**

### CSS Input File

```css
/* static/css/input.css */
@import "tailwindcss";

/* Source scanning - tells Tailwind where to find class usage */
@source "../internal/views/";
@source "../internal/handlers/";

/* Custom theme configuration with @theme directive */
@theme {
  /* Custom colors */
  --color-primary: #3b82f6;
  --color-secondary: #64748b;
  --color-accent: #8b5cf6;
  
  /* Custom fonts */
  --font-sans: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;
  
  /* Custom spacing */
  --spacing-18: 4.5rem;
  
  /* Custom animations */
  --animate-fade-in: fade-in 0.3s ease-out;
}

/* Custom utilities */
@utility content-auto {
  content-visibility: auto;
}

/* HTMX loading states */
.htmx-indicator {
  display: none;
}
.htmx-request .htmx-indicator {
  display: inline;
}
.htmx-request.htmx-indicator {
  display: inline;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

### @source Directives

Tailwind v4 scans files for class usage. Configure sources in CSS:

```css
/* Single directory */
@source "../internal/views/";

/* Multiple directories */
@source "../internal/views/";
@source "../internal/handlers/";
@source "./cmd/server/";

/* Glob patterns */
@source "../internal/**/*.templ";
```

### Build Commands

```bash
# Development (watch mode)
./tools/tailwindcss -i static/css/input.css -o static/css/output.css --watch

# Production (minified)
./tools/tailwindcss -i static/css/input.css -o static/css/output.css --minify

# With content polling (for some systems)
./tools/tailwindcss -i static/css/input.css -o static/css/output.css --watch --poll
```

### Project Structure

```
myapp/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── views/           # Templ files (scanned by Tailwind)
│   │   ├── layout.templ
│   │   └── pages.templ
│   └── handlers/
│       └── handler.go
├── static/
│   ├── css/
│   │   ├── input.css    # Tailwind source with @theme
│   │   └── output.css   # Generated CSS
│   └── js/
│       └── htmx.min.js
├── tools/
│   └── tailwindcss      # Standalone binary
└── justfile
```

### Using Tailwind Classes in Templ

```go
templ Button(text string, variant string) {
    <button class={ 
        "px-4 py-2 rounded font-medium transition-colors",
        templ.KV("bg-primary text-white hover:bg-primary/90", variant == "primary"),
        templ.KV("bg-secondary text-white hover:bg-secondary/90", variant == "secondary"),
        templ.KV("border border-current hover:bg-gray-100", variant == "outline"),
    }>
        { text }
    </button>
}
```

---

