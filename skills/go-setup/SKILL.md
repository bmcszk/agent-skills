---
name: go-setup
description: 'Go project setup, structure decisions, and library selection for production-ready applications. Use when starting a new Go project, deciding on project structure, choosing libraries, or setting up build tools. Covers CLI/TUI, single service, monorepo, mixed layouts, and recommended libraries. Keywords: go project setup, go project structure, go monorepo, go workspace, go libraries, go architecture.'
license: MIT
metadata:
  audience: developers
  workflow: setup
  category: backend
  technologies: go, architecture, project-structure
---

## What I do

I help with Go project initialization and setup:
- Project structure decisions
- Library selection
- Architecture planning
- Configuration setup

## When to use me

Use this skill when:
- Starting a new Go project
- Deciding on project structure
- Choosing libraries and dependencies
- Setting up build tools and configuration

---


## Project Structure References

Detailed structure guides are split into focused reference files:

- [CLI / TUI Applications](references/cli.md) — Simple CLI, supporting packages, TUI with Bubble Tea
- [Single Service](references/service.md) — Basic service, service with database, service layer responsibilities
- [Monorepo](references/monorepo.md) — go.work, multi-service justfile, CI
- [Mixed](references/mixed.md) — Combined CLI + service + shared packages layout
- [Recommended Libraries](references/libraries.md) — Core, CLI/TUI, database, concurrency, testing, build tools

## Common Commands

```bash
just build          # Build binary
just run            # Run application
just dev            # Run with hot reload

just check          # vet + test-unit + lint
just lint           # golangci-lint
just test-unit      # Unit tests only
just test-all       # All tests

just migrate-up     # Apply migrations
just migrate-down   # Rollback migrations
just sqlc           # Generate SQL code
```

## Standard justfile Template

```just
# Variables
binary := "myapp"
main := "./cmd/server"

# Default recipe (runs with just `just`)
default: build

# Build binary
build:
    go build -o bin/{{binary}} {{main}}

# Run application
run:
    go run {{main}}

# Development with hot reload (requires air)
dev:
    air

# Run all checks
check: lint test

# Run linter
lint:
    golangci-lint run ./...

# Run unit tests
test:
    go test -v -race ./...

# Run unit tests with coverage
test-coverage:
    go test -v -race -coverprofile=coverage.out ./...
    go tool cover -html=coverage.out -o coverage.html

# Run integration tests
test-integration:
    go test -v ./test/integration/...

# Run E2E tests
test-e2e:
    go test -v ./test/e2e/...

# Run all tests
test-all: test test-integration test-e2e

# Database migrations
migrate-up:
    migrate -path ./db/migrations -database "$DATABASE_URL" up

migrate-down:
    migrate -path ./db/migrations -database "$DATABASE_URL" down

# Generate SQL code
sqlc:
    sqlc generate

# Clean build artifacts
clean:
    rm -rf bin/
    rm -f coverage.out coverage.html

# Install binary to GOPATH
install:
    go install {{main}}
```

---

# Configuration

## Environment Variables (Recommended)

```go
package config

import "github.com/caarlos0/env/v11"

type Config struct {
    Port         int    `env:"PORT" envDefault:"8080"`
    DatabaseURL  string `env:"DATABASE_URL" envRequired:"true"`
    LogLevel     string `env:"LOG_LEVEL" envDefault:"info"`
    JWTSecret    string `env:"JWT_SECRET" envRequired:"true"`
}

func Load() (*Config, error) {
    cfg := &Config{}
    if err := env.Parse(cfg); err != nil {
        return nil, err
    }
    return cfg, nil
}
```

## .env Files (Development Only)

```
# .env (gitignored)
DATABASE_URL=postgres://user:pass@localhost:5432/mydb
JWT_SECRET=dev-secret
LOG_LEVEL=debug
PORT=8080
```

---

# Key Principles

## From Official Go Docs

1. **Start simple** - Single `main.go` is fine for small projects
2. **Use `internal/`** for private packages (enforced by compiler)
3. **Use `cmd/`** for multiple binaries
4. **Use `pkg/`** only for packages meant to be imported by others
5. **Never use `/src`** - this is a Java pattern, not Go

## Common Mistakes to Avoid

| ❌ Don't | ✅ Do |
|---------|-------|
| Create `/src` directory | Use root or `cmd/` |
| Over-engineer small projects | Start simple, evolve |
| Create packages just to organize files | Create packages for logical boundaries |
| Copy Java/Python structures | Follow Go conventions |
| Premature abstraction | Wait until you need it |

## When to Create a New Package

Create a new package when:
- Code needs to be **reused** in multiple places
- You want to **enforce a boundary** between code
- It reduces **cognitive overhead** as a "black box"

Don't create a package just to:
- Organize files
- Reduce file size
- Match structure from other languages

---

# Initialization Checklist

When starting a new Go project:

1. [ ] Initialize go module: `go mod init github.com/org/project`
2. [ ] Choose structure based on project type
3. [ ] Add justfile
4. [ ] Configure golangci-lint
5. [ ] Set up CI/CD (GitHub Actions)
6. [ ] Add .gitignore
7. [ ] Create README.md
8. [ ] Set up database migrations (if needed)
9. [ ] Configure sqlc (if using)
10. [ ] Add base tests

---

# .gitignore for Go

```
# Binaries
*.exe
*.exe~
*.dll
*.so
*.dylib
bin/

# Test
*.test
*.out
coverage.out

# Go workspace
go.work
go.work.sum

# Environment
.env
.env.local
*.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# Build
dist/
```

---

# CI/CD Example (GitHub Actions)

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      
      - uses: extractions/setup-just@v2
      
      - name: Download dependencies
        run: go mod download
      
      - name: Run checks
        run: just check
      
      - name: Run all tests
        run: just test-all
```

---

# Related Skills

After setup, use these skills for development:
- `go-dev` - Go development patterns and best practices
- `go-fluent-testing` - Unit/integration/E2E testing (fluent Given/When/Then)
