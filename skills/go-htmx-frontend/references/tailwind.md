# Tailwind CSS v4

Docs: https://tailwindcss.com/blog/tailwindcss-v4 and https://tailwindcss.com/blog/standalone-cli

Tailwind v4 configures in CSS. There is no `tailwind.config.js`.

## Install the standalone CLI

Use the standalone binary. It needs no `node_modules`, `package.json`, or lock file.

Release asset names (checked against https://github.com/tailwindlabs/tailwindcss/releases/latest, v4.3.3):

| Platform | Asset |
|----------|-------|
| Linux x64 | `tailwindcss-linux-x64` |
| Linux arm64 | `tailwindcss-linux-arm64` |
| macOS arm64 | `tailwindcss-macos-arm64` |

Other assets exist: `-linux-x64-musl`, `-linux-arm64-musl` (Alpine), `-macos-x64`, `-windows-x64.exe`. The old `tailwindcss-<arch>-unknown-linux-gnu` names do not exist in v4. Recheck the asset list when you upgrade.

```bash
os="$(uname -s)-$(uname -m)"
case "$os" in
    Linux-x86_64)  asset=tailwindcss-linux-x64 ;;
    Linux-aarch64) asset=tailwindcss-linux-arm64 ;;
    Darwin-arm64)  asset=tailwindcss-macos-arm64 ;;
    *) echo "unsupported platform: $os" >&2; exit 1 ;;
esac

mkdir -p tools
curl -fsSL "https://github.com/tailwindlabs/tailwindcss/releases/latest/download/$asset" -o tools/tailwindcss
chmod +x tools/tailwindcss
```

`curl -f` makes a wrong asset name fail the command. Without it, curl saves the 404 page as the binary. For a repeatable build, replace `latest/download` with `download/v4.3.3` (the version you tested) and check the file against `sha256sums.txt` from the same release.

## CSS input file

```css
/* static/css/input.css */
@import "tailwindcss";

@source "../../internal/views/";
@source "../../internal/handlers/";

@theme {
  --color-primary: #3b82f6;
  --color-secondary: #64748b;
  --color-accent: #8b5cf6;

  --font-sans: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  --spacing-18: 4.5rem;

  --animate-fade-in: fade-in 0.3s ease-out;
}

@utility content-auto {
  content-visibility: auto;
}

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

## @source paths

`@source` paths resolve relative to the CSS file, not to the project root or the shell directory. With the CSS in `static/css/`, the project root is `../../`.

```css
/* static/css/input.css */
@source "../../internal/views/";
@source "../../internal/handlers/";
@source "../../cmd/server/";
@source "../../internal/**/*.templ";
```

Tailwind also scans the working directory on its own and skips files that `.gitignore` lists. Add `@source` for code outside the working directory, or for code in an ignored path.

## Build commands

```bash
# Development (watch mode)
./tools/tailwindcss -i static/css/input.css -o static/css/output.css --watch

# Production (minified)
./tools/tailwindcss -i static/css/input.css -o static/css/output.css --minify

# Watch with polling, for network or container file systems that send no change events
./tools/tailwindcss -i static/css/input.css -o static/css/output.css --watch --poll
```

`--poll` exists in v4 (`Use polling instead of filesystem events when watching`). It takes an optional interval in milliseconds (default 250), written `--poll=500`. It has an effect only together with `--watch`.

## Project structure

```text
myapp/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── views/           # Templ files
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

## Classes in Templ

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

Write each class as a whole string. Tailwind finds classes by scanning text, so a class built with string concatenation (`"bg-" + color`) is never generated.
