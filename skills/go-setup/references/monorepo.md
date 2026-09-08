# Monorepo (Multiple Services)
# 3. Monorepo (Multiple Services)

Uses Go workspaces (`go.work`) for managing multiple modules.

```
myorg/
├── go.work
├── go.work.sum
├── services/
│   ├── user-service/
│   │   ├── go.mod
│   │   ├── cmd/
│   │   │   └── server/
│   │   │       └── main.go
│   │   ├── internal/
│   │   │   ├── handler/
│   │   │   ├── service/
│   │   │   ├── repository/
│   │   │   └── model/
│   │   ├── db/
│   │   │   ├── migrations/
│   │   │   └── queries/
│   │   └── test/
│   │       ├── integration/
│   │       └── e2e/
│   ├── payment-service/
│   │   ├── go.mod
│   │   ├── cmd/
│   │   ├── internal/
│   │   ├── db/
│   │   └── test/
│   └── notification-service/
│       ├── go.mod
│       └── ...
├── pkg/                    # Shared public packages
│   ├── logger/
│   │   └── logger.go
│   ├── httputil/
│   │   └── httputil.go
│   └── config/
│       └── config.go
├── internal/               # Shared private packages
│   └── database/
│       └── postgres.go
├── proto/                  # Protocol definitions (gRPC)
│   ├── user/
│   │   └── user.proto
│   └── payment/
│       └── payment.proto
├── test/                   # Shared test utilities
│   ├── fixtures/
│   └── testutil/
├── docs/
├── scripts/
│   ├── build.sh
│   └── deploy.sh
├── docker-compose.yml
├── justfile
└── README.md
```

### go.work Example

```go
go 1.22

use (
    ./services/user-service
    ./services/payment-service
    ./services/notification-service
)
```

### Monorepo justfile

```just
# Variables
services := "user-service payment-service notification-service"

# Default recipe
default: build test

# Build all services
build:
    @for svc in {{services}}; do \
        echo "Building $$svc..."; \
        just -f services/$$svc/justfile build; \
    done

# Test all services
test:
    @for svc in {{services}}; do \
        echo "Testing $$svc..."; \
        just -f services/$$svc/justfile test; \
    done

# Lint all code
lint:
    golangci-lint run ./...

# Run integration tests
test-integration:
    @for svc in {{services}}; do \
        just -f services/$$svc/justfile test-integration; \
    done
```

---

