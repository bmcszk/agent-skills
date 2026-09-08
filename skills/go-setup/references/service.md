# Single Service (API / Backend)
# 2. Single Service (API / Backend)

## Basic Service

```
myservice/
├── go.mod
├── main.go
├── internal/
│   ├── handler/         # HTTP handlers
│   │   ├── handler.go
│   │   ├── user.go
│   │   └── health.go
│   ├── service/         # Business logic
│   │   └── user.go
│   ├── repository/      # Data access
│   │   └── user.go
│   ├── model/           # Domain models
│   │   └── user.go
│   └── config/
│       └── config.go
├── test/
│   ├── integration/
│   │   ├── integration_test.go
│   │   └── integration_parts_test.go
│   └── e2e/
│       ├── e2e_test.go
│       └── e2e_parts_test.go
├── README.md
└── justfile
```

## Service with Database

```
myservice/
├── go.mod
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handler/
│   ├── service/
│   ├── repository/
│   ├── model/
│   └── config/
├── db/
│   ├── migrations/
│   │   ├── 001_create_users.up.sql
│   │   └── 001_create_users.down.sql
│   └── queries/
│       └── users.sql
├── api/
│   └── openapi.yaml
├── test/
│   ├── integration/
│   └── e2e/
├── docker-compose.yml
├── Dockerfile
├── README.md
└── justfile
```

## Service Layer Responsibilities

| Layer | Responsibility | Dependencies |
|-------|---------------|--------------|
| `handler/` | HTTP handling, validation | service/ |
| `service/` | Business logic, orchestration | repository/, model/ |
| `repository/` | Data access, persistence | model/ |
| `model/` | Domain entities, pure | None |
| `config/` | Configuration loading | None |

---

# 3. Monorepo (Multiple Services)

Uses Go workspaces (`go.work`) for managing multiple modules.

```
myorg/
├── go.work
├── go.work.sum
├── services/
│   ├── user-service/
│   │   ├── go.mod
