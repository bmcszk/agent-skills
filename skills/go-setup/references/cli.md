# CLI / TUI Applications
# Project Structure Decision Matrix

| Project Type | Recommended Structure | Key Pattern |
|--------------|----------------------|-------------|
| CLI / TUI App | Basic + internal/ | Flat, simple |
| Single Service | cmd/ + internal/ | Server layout |
| Monorepo | go.work + services/ | Workspaces |
| Mixed (CLI + Service) | cmd/ + internal/ | Combined layout |

---

# 1. CLI / TUI Application

## Simple CLI (1-5 files)

Keep everything in root directory. No nesting.

```
mycli/
├── go.mod
├── main.go
├── cli.go           # CLI logic
├── cli_test.go
├── config.go        # Configuration
├── README.md
└── justfile
```

## CLI with Supporting Packages

```
mycli/
├── go.mod
├── main.go              # Entry point only
├── internal/
│   ├── cmd/             # Command implementations
│   │   ├── root.go
│   │   ├── root_test.go
│   │   ├── version.go
│   │   └── list.go
│   ├── config/          # Configuration handling
│   │   └── config.go
│   └── output/          # Output formatting
│       └── output.go
├── README.md
└── justfile
```

## TUI Application (Bubble Tea)

```
mytui/
├── go.mod
├── main.go
├── internal/
│   ├── app/             # Main TUI application
│   │   ├── app.go       # tea.Model implementation
│   │   ├── app_test.go
│   │   ├── update.go    # Update function
│   │   └── view.go      # View function
│   ├── components/      # Reusable UI components
│   │   ├── list/
│   │   │   └── list.go
│   │   ├── input/
│   │   │   └── input.go
│   │   └── spinner/
│   │       └── spinner.go
│   ├── styles/          # Lipgloss styles
│   │   └── styles.go
│   └── config/
│       └── config.go
├── README.md
└── justfile
```

### TUI Libraries

| Purpose | Library | Import |
|---------|---------|--------|
| TUI Framework | bubbletea | `github.com/charmbracelet/bubbletea` |
| Styling | lipgloss | `github.com/charmbracelet/lipgloss` |
| Bubbles | bubbles | `github.com/charmbracelet/bubbles` |
| CLI Flags | cobra | `github.com/spf13/cobra` |
| Configuration | viper | `github.com/spf13/viper` |
| Progress bars | progress | `github.com/charmbracelet/bubbles/progress` |

---

# 2. Single Service (API / Backend)

## Basic Service

```
myservice/
├── go.mod
├── main.go
├── internal/
│   ├── handler/         # HTTP handlers
