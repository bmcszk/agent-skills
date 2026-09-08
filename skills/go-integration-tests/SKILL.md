---
name: go-integration-tests
description: 'Go integration testing with testcontainers, real dependencies, and fluent Given/When/Then structure. Use when testing component interactions, real databases, or service integrations. Follows mandatory fluent-testing-guideline.md pattern. Runs in test/integration/. Keywords: integration testing, testcontainers, real database test, fluent testing, given when then, service integration.'
license: MIT
metadata:
  audience: developers
  workflow: testing
  category: integration-testing
  technologies: go, testcontainers, docker
---

## What I do

Integration testing with real dependencies using testcontainers and fluent Given/When/Then pattern.

## MANDATORY Reference

**ALL integration tests MUST follow:**
`references/fluent-testing-guideline.md` (included in this skill directory)

## When to use me

- Testing component interactions
- Testing with real databases
- Testing service integrations

## Rules

### Location
- **Directory**: `test/integration/`
- **Package**: `package integration_test`
- **Build Tags**: DO NOT USE

### Fluent Test Structure (MANDATORY)

```go
func TestService_DatabaseIntegration(t *testing.T) {
    given, when, then := newParts(t)

    given.
        postgresContainer().and().
        initializeService()

    when.
        processData()

    then.
        resultIsValid().and().
        noError()
}
```

### Parts Struct Pattern

```go
type parts struct {
    *testing.T
    require    *require.Assertions
    container  testcontainers.Container
    db         *sql.DB
    configFile string
    response   any
}

func newParts(t *testing.T) (*parts, *parts, *parts) {
    t.Helper()
    p := &parts{
        T:       t,
        require: require.New(t),
    }
    p.setupTestEnvironment()
    return p, p, p  // given, when, then
}

func (p *parts) and() *parts { return p }
```

### Given Methods (Setup)

```go
func (p *parts) postgresContainer() *parts {
    ctx := context.Background()
    
    req := testcontainers.ContainerRequest{
        Image:        "postgres:15",
        ExposedPorts: []string{"5432/tcp"},
        Env: map[string]string{
            "POSTGRES_USER":     "test",
            "POSTGRES_PASSWORD": "test",
            "POSTGRES_DB":       "testdb",
        },
        WaitingFor: wait.ForLog("database system is ready"),
    }
    
    container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: req,
        Started:          true,
    })
    p.require.NoError(err)
    
    p.container = container
    return p
}

func (p *parts) initializeService() *parts {
    connStr, _ := p.container.Endpoint(ctx, "")
    p.db, _ = sql.Open("postgres", connStr)
    return p
}
```

### When Methods (Action)

```go
func (p *parts) processData() *parts {
    service := NewService(p.db)
    var err error
    p.response, err = service.ProcessData()
    p.require.NoError(err)
    return p
}
```

### Then Methods (Verification)

```go
func (p *parts) resultIsValid() *parts {
    p.require.NotNil(p.response)
    return p
}

func (p *parts) noError() *parts {
    p.require.NoError(p.checks.repeatRun())
    return p
}
```

### Async Check Pattern

```go
type checks struct {
    interval time.Duration
    timeout  time.Duration
    checks   []*check
}

func newChecks() *checks {
    interval := 500 * time.Millisecond
    timeout := 20 * time.Second
    
    if os.Getenv("CI") == "true" {
        interval = 2 * time.Second
        timeout = 60 * time.Second
    }
    
    return &checks{interval: interval, timeout: timeout}
}
```

### Cleanup Pattern

```go
func (p *parts) cleanupDatabase() *parts {
    if p.db == nil {
        p.Log("Warning: database connection is nil, skipping cleanup")
        return p
    }
    _, _ = p.db.Exec("DELETE FROM users")
    return p
}
```

## Critical Rules from fluent-testing-guideline.md

### FORBIDDEN Patterns

```go
// ❌ NEVER: Direct helper function call
configFile := createTestConfigFile(t)

// ❌ NEVER: Local variables for test state
userID := "123"

// ❌ NEVER: Multiple given statements
given.setupDatabase()
given.createTestData()

// ❌ NEVER: .and() at wrong position
when.
    executeAction()
        .and().validateResult()  // WRONG
```

### REQUIRED Patterns

```go
// ✅ ALWAYS: Given/When/Then structure
given, when, then := newParts(t)

given.
    setupDatabase().and().
    createTestData()

when.
    executeAction()

then.
    verifyResult().and().
    noError()

// ✅ ALWAYS: Single given chain
given.
    postgresContainer().and().
    initializeService()

// ✅ ALWAYS: .and() at end of line
then.
    resultIsValid().and().
    noError()
```

## Standards

- **Speed**: 100ms-1s per test
- **Dependencies**: testcontainers for real services
- **Cleanup**: Always clean up after tests
- **Structure**: Fluent Given/When/Then (MANDATORY)

## Commands

```bash
<runner> test-integration

# Use project's runner: make or just
```

## Forbidden

- NEVER skip cleanup
- NEVER leave containers running
- NEVER use build tags
- NEVER use direct helper function calls
- NEVER create local variables for test state
- NEVER skip Given/When/Then structure
- NEVER use multiple separate given statements
