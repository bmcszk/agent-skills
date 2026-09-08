---
name: go-e2e-tests
description: 'Go E2E testing with fluent Given/When/Then pattern, docker-compose, and HTTP testing. Use when testing complete user workflows, API contracts, or multi-service integrations. Follows mandatory fluent-testing-guideline.md pattern. Runs in test/e2e/ with docker-compose. Keywords: e2e testing, end-to-end test, fluent testing, given when then, docker-compose test, integration test.'
license: MIT
metadata:
  audience: developers
  workflow: testing
  category: e2e-testing
  technologies: go, docker-compose, http
---

## What I do

E2E testing with fluent Given/When/Then structure and Docker Compose.

## MANDATORY Reference

**ALL E2E tests MUST follow:**
`references/fluent-testing-guideline.md` (included in this skill directory)

## When to use me

- Testing complete user workflows
- Testing API contracts
- Testing across multiple services

## Rules

### Location
- **Directory**: `test/e2e/`
- **Package**: `package e2e_test`
- **Build Tags**: DO NOT USE

### Architecture
- Services run in Docker Compose
- Tests run on host machine
- Tests connect to exposed ports

## Fluent Builder Pattern (MANDATORY)

### Parts Struct

```go
type parts struct {
    *testing.T
    require      *require.Assertions
    configFile   string
    userID       string
    responseCode int
    responseBody []byte
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

func TestComplexWorkflow(t *testing.T) {
    given, when, then := newParts(t)

    given.
        setupScenario().and().
        configureServices().and().
        initializeClient()

    when.
        executeAction().and().
        waitForResponse()

    then.
        verifyResult().and().
        checkSideEffects().and().
        noError()
}
```

## Given Methods (Setup)

```go
// Configuration
func (p *parts) unifiedConfigFile() *parts {
    p.configFile = createAndStoreConfig(p.T)
    p.setupScenarioTestServer(p.configFile)
    return p
}

// Database setup
func (p *parts) setupDatabase() *parts {
    p.db = setupTestDatabase(p.T)
    return p
}

// Test data
func (p *parts) createTestData() *parts {
    p.userID = "test-user-123"
    _, err := p.db.Exec("INSERT INTO users (id) VALUES ($1)", p.userID)
    p.require.NoError(err)
    return p
}

// Service configuration
func (p *parts) configureServices() *parts {
    p.httpClient = &http.Client{Timeout: 10 * time.Second}
    return p
}
```

## When Methods (Action)

```go
// HTTP requests
func (p *parts) createResourceViaAPI() *parts {
    resp, err := p.httpClient.Post(
        "http://"+p.serviceAddress+"/api/resources",
        "application/json",
        bytes.NewReader(p.requestBody),
    )
    p.require.NoError(err)
    p.responseCode = resp.StatusCode
    p.responseBody, _ = io.ReadAll(resp.Body)
    return p
}

// Async actions
func (p *parts) executeAction() *parts {
    // Store result in parts, don't validate here
    p.lastError = p.service.Execute()
    return p
}

// Message sending
func (p *parts) sendAssetEvent(eventType, videoID string) *parts {
    return p.sendMessageFromTemplate("asset_event.json", map[string]any{
        "Type":          eventType,
        "ExternalUUID":  videoID,
    })
}
```

## Then Methods (Verification)

```go
// Response validation
func (p *parts) resourceCreatedSuccessfully() *parts {
    p.require.Equal(http.StatusCreated, p.responseCode)
    return p
}

func (p *parts) responseContains(expected string) *parts {
    p.require.Contains(string(p.responseBody), expected)
    return p
}

// Async checks (use checks pattern)
func (p *parts) videoHasStatus(expectedStatus string) *parts {
    p.checks.add(func() error {
        resp, err := p.httpClient.Get(p.serviceAddress + "/videos/" + p.videoID)
        if err != nil {
            return fmt.Errorf("get video: %w", err)
        }
        defer resp.Body.Close()
        
        var video struct { Status string `json:"status"` }
        json.NewDecoder(resp.Body).Decode(&video)
        
        if video.Status != expectedStatus {
            return fmt.Errorf("expected status %s, got %s", expectedStatus, video.Status)
        }
        return nil
    })
    return p
}

func (p *parts) noError() *parts {
    p.require.NoError(p.checks.repeatRun())
    return p
}
```

## Async Check Pattern

```go
type checks struct {
    interval time.Duration
    timeout  time.Duration
    checks   []*check
}

type check struct {
    f   func() error
    ok  bool
    err error
}

func newChecks() *checks {
    interval := 500 * time.Millisecond
    timeout := 20 * time.Second
    
    if os.Getenv("CI") == "true" || os.Getenv("GITHUB_ACTIONS") == "true" {
        interval = 2 * time.Second
        timeout = 60 * time.Second
    }
    
    return &checks{
        interval: interval,
        timeout:  timeout,
        checks:   make([]*check, 0, 10),
    }
}

func (cs *checks) add(f func() error) {
    cs.checks = append(cs.checks, &check{f: f})
}

func (cs *checks) repeatRun() error {
    tick := time.Tick(cs.interval)
    limit := time.After(cs.timeout)
    
    for {
        select {
        case <-limit:
            return cs.error()
        case <-tick:
            cs.run()
            if cs.ok() {
                return nil
            }
        }
    }
}
```

## Critical Rules from fluent-testing-guideline.md

### FORBIDDEN Patterns

```go
// ❌ NEVER: Direct helper function call
configFile := createTestUnifiedConfigFile(t)

// ❌ NEVER: Local variables for test state
userID := "123"

// ❌ NEVER: Multiple given statements
given.setupDatabase()
given.createTestData()

// ❌ NEVER: .and() at wrong position
when.
    executeAction()
        .and().validateResult()

// ❌ NEVER: Validation in when section
when.
    executeAction().and().
    verifyResult()  // WRONG: validation belongs in then

// ❌ NEVER: Missing then section
given, when, _ := newParts(t)
```

### REQUIRED Patterns

```go
// ✅ ALWAYS: Given/When/Then structure
given, when, then := newParts(t)

given.
    setupScenario().and().
    configureServices()

when.
    executeAction()

then.
    verifyResult().and().
    noError()

// ✅ ALWAYS: All state in parts struct
type parts struct {
    *testing.T
    configFile string  // State in parts
    userID     string  // State in parts
    response   *http.Response
}

// ✅ ALWAYS: Single given chain
given.
    setupDatabase().and().
    createTestData().and().
    configureServices()

// ✅ ALWAYS: .and() at end of line
then.
    resultIsValid().and().
    noError()

// ✅ ALWAYS: Declare only used sections
func TestSimpleAction(t *testing.T) {
    _, when, then := newParts(t)  // No given needed
    when.executeAction()
    then.verifyResult()
}
```

## Test Structure

```
test/
└── e2e/
    ├── .env.test              # Test environment config
    ├── docker-compose.test.yml
    ├── templates/              # Test data templates
    │   └── asset_event.json
    ├── e2e_test.go            # Test scenarios
    ├── e2e_parts_test.go      # Parts struct and fluent methods
    └── e2e_checks_test.go     # Async check implementation
```

## Commands

```bash
<runner> test-e2e-up    # Start services
<runner> test-e2e-run   # Run tests
<runner> test-e2e-down  # Stop services
<runner> test-e2e       # Complete workflow

# Use project's runner: make or just
```

## Forbidden

- NEVER declare unused variables
- NEVER use direct helper calls - use fluent methods
- NEVER create local variables for test state
- NEVER use build tags
- NEVER skip Given/When/Then structure
- NEVER put validation in when section
- NEVER use multiple separate given statements
- NEVER position .and() incorrectly
