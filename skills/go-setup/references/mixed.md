# Mixed (CLI + Service + Shared Packages)
# 4. Mixed (CLI + Service + Shared Packages)

Combines multiple binaries with shared code.

```
myproject/
├── go.mod
├── cmd/
│   ├── server/            # HTTP server
│   │   └── main.go
│   ├── cli/               # CLI tool
│   │   └── main.go
│   └── worker/            # Background worker
│       └── main.go
├── internal/
│   ├── handler/           # HTTP handlers (server only)
│   ├── service/           # Business logic (shared)
│   ├── repository/        # Data access (shared)
│   ├── model/             # Domain models (shared)
│   ├── config/            # Configuration (shared)
│   └── worker/            # Worker logic (worker only)
├── pkg/                   # Public packages (if needed)
│   └── api/
│       └── client.go
├── api/
│   └── openapi.yaml
├── db/
│   ├── migrations/
│   └── queries/
├── test/
│   ├── integration/
│   │   ├── integration_test.go
│   │   └── integration_parts_test.go
│   └── e2e/
│       ├── e2e_test.go
│       └── e2e_parts_test.go
├── docker-compose.yml
├── Dockerfile
├── justfile
└── README.md
```

### Mixed Project justfile

```just
# Default recipe
default: build test

# Build all binaries
build: build-server build-cli build-worker

build-server:
    go build -o bin/server ./cmd/server

build-cli:
    go build -o bin/cli ./cmd/cli

build-worker:
    go build -o bin/worker ./cmd/worker

# Run tests
test:
    go test -v ./...

test-integration:
    go test -v ./test/integration/...

test-e2e:
    go test -v ./test/e2e/...

# Run applications
run-server:
    go run ./cmd/server

run-cli:
    go run ./cmd/cli

run-worker:
    go run ./cmd/worker
```

---

