---
name: go-tester
description: 'Go integration and E2E testing with testcontainers, docker-compose, and fluent Given/When/Then patterns. Use when testing component interactions, complete workflows, or with real databases/services. Hub skill pointing to go-integration-tests and go-e2e-tests for detailed patterns. Keywords: go testing, integration test, e2e test, testcontainers, docker-compose, fluent testing.'
license: MIT
metadata:
  audience: developers
  workflow: testing
  category: testing
  technologies: go, testcontainers, docker-compose
---

## What I do

Integration and E2E testing with real dependencies using fluent Given/When/Then pattern.

## MANDATORY Reference

**ALL integration and E2E tests MUST follow:**
`references/fluent-testing-guideline.md` (included in this skill directory)

## Related Skills

- `go-integration-tests` - Detailed integration test patterns
- `go-e2e-tests` - Detailed E2E test patterns

## When to use me

- Testing component interactions
- Testing complete workflows
- Testing with real databases/services

## Fluent Pattern (MANDATORY)

### Parts Struct

```go
type parts struct {
    *testing.T
    require      *require.Assertions
    configFile   string
    userID       string
    response     *http.Response
    responseCode int
    checks       *checks
}

func newParts(t *testing.T) (*parts, *parts, *parts) {
    t.Helper()
    p := &parts{
        T:       t,
        require: require.New(t),
        checks:  newChecks(),
    }
    p.setupTestEnvironment()
    return p, p, p  // given, when, then
}

func (p *parts) and() *parts { return p }
```

### Test Structure

```go
func TestAPI_ResourceCreation(t *testing.T) {
    given, when, then := newParts(t)

    given.
        unifiedConfigFile()

    when.
        createResourceViaAPI()

    then.
        resourceCreatedSuccessfully().and().
        noError()
}
```

## Integration Tests

### Location
- **Directory**: `test/integration/`
- **Package**: `package integration_test`

### Pattern
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

## E2E Tests

### Location
- **Directory**: `test/e2e/`
- **Package**: `package e2e_test`

### Pattern
```go
func TestFeature_Workflow(t *testing.T) {
    given, when, then := newParts(t)

    given.
        setupScenario().and().
        configureServices()

    when.
        executeAction()

    then.
        verifyResult().and().
        noError()
}
```

## Async Check Pattern

```go
func newChecks() *checks {
    interval := 500 * time.Millisecond
    timeout := 20 * time.Second
    
    if os.Getenv("CI") == "true" {
        interval = 2 * time.Second
        timeout = 60 * time.Second
    }
    
    return &checks{interval: interval, timeout: timeout}
}

func (p *parts) noError() *parts {
    p.require.NoError(p.checks.repeatRun())
    return p
}
```

## Critical Rules

### From fluent-testing-guideline.md

1. **Given/When/Then Structure**
   - ALWAYS use all three sections
   - NEVER skip the `then` section

2. **No Direct Helper Calls**
   - ❌ `configFile := createConfigFile(t)`
   - ✅ `given.unifiedConfigFile()`

3. **All State in Parts**
   - ❌ Local variables for test state
   - ✅ Store in `parts` struct

4. **Single Given Chain**
   - ❌ Multiple separate `given.` statements
   - ✅ One chain: `given.setup().and().configure()`

5. **Proper Formatting**
   ```go
   // ✅ CORRECT
   given.
       setupScenario().and().
       configureServices()

   when.
       executeAction()

   then.
       verifyResult().and().
       noError()
   ```

## Commands

```bash
<runner> test-integration
<runner> test-e2e-up     # Start services
<runner> test-e2e-run    # Run tests
<runner> test-e2e-down   # Stop services
<runner> test-e2e        # Complete workflow
```

## Rules

- Use testcontainers for real DBs
- Use docker-compose for services
- Always cleanup containers
- No mocks for integration/E2E
- MANDATORY: Given/When/Then structure
- MANDATORY: All state in parts struct
- MANDATORY: Single given chain

## Forbidden

- NEVER skip cleanup
- NEVER leave containers running
- NEVER use build tags
- NEVER use direct helper function calls
- NEVER create local variables for test state
- NEVER skip Given/When/Then structure
- NEVER use multiple separate given statements
