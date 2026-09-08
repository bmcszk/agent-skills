# Deployment & Build
## justfile

```just
# Variables
binary_name := "server"
build_dir := "bin"
tailwind_bin := "./tools/tailwindcss"
css_input := "static/css/input.css"
css_output := "static/css/output.css"

# Default: show available commands
default:
    @just --list

# Install dependencies (templ + tailwind standalone)
install:
    go install github.com/a-h/templ/cmd/templ@latest
    @mkdir -p tools
    @curl -sL https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-$(uname -m)-unknown-linux-gnu -o {{tailwind_bin}}
    @chmod +x {{tailwind_bin}}

# Development mode with hot reload
dev:
    #!/bin/bash
    set -e
    trap 'kill $(jobs -p)' EXIT
    templ generate -watch -proxy="http://localhost:3000" -proxyport="8080" -cmd="go run ./cmd/server" &
    {{tailwind_bin}} -i {{css_input}} -o {{css_output}} --watch &
    wait

# Build for production
build:
    templ generate
    {{tailwind_bin}} -i {{css_input}} -o {{css_output}} --minify
    go build -o {{build_dir}}/{{binary_name}} ./cmd/server

# Generate templ files only
gen:
    templ generate

# Build CSS only
css:
    {{tailwind_bin}} -i {{css_input}} -o {{css_output}} --minify

# Build CSS in watch mode
css-watch:
    {{tailwind_bin}} -i {{css_input}} -o {{css_output}} --watch

# Run all tests
test:
    go test ./...

# Run tests with coverage
test-coverage:
    go test -cover ./...

# Format code
fmt:
    templ fmt .
    go fmt ./...

# Lint
lint:
    golangci-lint run

# Clean build artifacts
clean:
    rm -rf {{build_dir}}/
    find . -name "*_templ.go" -delete
    rm -f {{css_output}}

# Full CI check
check: fmt lint test
    templ generate
    go build ./...
```

---

## Commands

```bash
# Development
just dev              # Start dev server with hot reload (templ + tailwind watch)
just gen              # Generate templ files only
just css              # Build CSS once
just css-watch        # Watch CSS changes

# Production
just build            # Full production build

# Quality
just test             # Run tests
just test-coverage    # Run tests with coverage
just fmt              # Format all code
just lint             # Run linter
just check            # Full CI check

# Cleanup
just clean            # Remove build artifacts

# Direct Tailwind commands
./tools/tailwindcss -i static/css/input.css -o static/css/output.css --minify
./tools/tailwindcss -i static/css/input.css -o static/css/output.css --watch
```

---

