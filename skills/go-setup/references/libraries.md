# Recommended Libraries

## Core Libraries

| Purpose | Library | Import | Notes |
|---------|---------|--------|-------|
| HTTP Router | chi | `github.com/go-chi/chi/v5` | Lightweight, stdlib-compatible |
| Testing | testify | `github.com/stretchr/testify` | assert, require, mock, suite |
| Config | caarlos0/env | `github.com/caarlos0/env/v11` | Environment-based config |
| Logging | slog | `log/slog` | Go 1.21+ stdlib |

## CLI / TUI Libraries

| Purpose | Library | Import | Notes |
|---------|---------|--------|-------|
| CLI Framework | cobra | `github.com/spf13/cobra` | Full-featured CLI |
| CLI (simple) | urfave/cli | `github.com/urfave/cli/v3` | Simple CLI apps |
| TUI Framework | bubbletea | `github.com/charmbracelet/bubbletea` | Elm-style TUI |
| Styling | lipgloss | `github.com/charmbracelet/lipgloss` | TUI styling |
| UI Components | bubbles | `github.com/charmbracelet/bubbles` | Pre-built components |

## Database

| Purpose | Library | Import | Notes |
|---------|---------|--------|-------|
| SQL Generator | sqlc | `github.com/sqlc-dev/sqlc` | Type-safe SQL |
| Migrations | golang-migrate | `github.com/golang-migrate/migrate/v4` | Database migrations |
| PostgreSQL Driver | pgx | `github.com/jackc/pgx/v5` | Pure Go PostgreSQL |

## Concurrency

| Purpose | Library | Import | Notes |
|---------|---------|--------|-------|
| Error Groups | errgroup | `golang.org/x/sync/errgroup` | Goroutines with error handling |

## Testing (Integration/E2E)

| Purpose | Library | Import | Notes |
|---------|---------|--------|-------|
| Testcontainers | testcontainers | `github.com/testcontainers/testcontainers-go` | Real dependencies |
| HTTP Testing | httptest | `net/http/httptest` | Stdlib HTTP testing |

## When to Use What

### HTTP Frameworks

| Need | Recommendation |
|------|----------------|
| Simple REST API | `chi` + stdlib |
| GraphQL | `gqlgen` |
| gRPC | `google.golang.org/grpc` |
| Full framework | Avoid - use stdlib + chi |

### Database Access

| Need | Recommendation |
|------|----------------|
| Type-safe SQL | `sqlc` (preferred) |
| Simple queries | `database/sql` + `pgx` |
| ORM needed | `gorm` (use sparingly) |
| Migrations | `golang-migrate` |

### Configuration

| Need | Recommendation |
|------|----------------|
| 12-factor app | `caarlos0/env` |
| Complex config | `koanf` |
| CLI config | `viper` |

---

# Build Tools

## just (Preferred)

[just](https://github.com/casey/just) is a modern command runner with better syntax than make.

Install:
```bash
# macOS
brew install just

# Linux
cargo install just
# or
brew install just
```

