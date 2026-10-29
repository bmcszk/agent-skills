# E2E test operations

## Migration Guidelines: Standard to E2E Tests

### 1. Migration Decision Matrix
**Use this guide to determine when to create E2E tests:**

| Test Need | Recommended Approach | Migration Strategy |
|-----------|---------------------|-----------------|
| Single function unit logic | **Unit Test** | Add unit tests if missing |
| Service interaction | **Integration Test** | Create integration tests |
| Complete user workflow | **E2E Test** | Create E2E test with Given/When/Then |
| API contract validation | **E2E Test** | Convert integration tests to E2E |
| Frontend user journey | **Browser Test** | Create browser tests with chromedp |

### 2. Standard Test to E2E Migration Process

**Step 1: Identify Migration Candidates**
```bash
# Find integration tests that cover user workflows
find test/integration -name "*integration_test.go" | \
    xargs grep -l "workflow\|journey\|end-to-end"
```

**Step 2: Analyze Current Test Structure**
```go
// BEFORE: Standard integration test
func TestUserService_CreateUser(t *testing.T) {
    db := setupTestDatabase(t)
    defer db.Close()

    service := NewUserService(db)
    user := &User{Name: "Test User", Email: "test@example.com"}

    created, err := service.CreateUser(user)
    assert.NoError(t, err)
    assert.Equal(t, user.Name, created.Name)
    assert.NotZero(t, created.ID)
}
```

**Step 3: Convert to Given/When/Then Structure**
```go
// AFTER: Migrated to E2E with fluent pattern
func TestUserService_CreateUser(t *testing.T) {
    given, when, then := newParts(t)

    given.
        setupTestDatabase().and().
        initializeUserService()

    when.
        createUserWithName("Test User").and().
        createUserWithEmail("test@example.com")

    then.
        userCreatedSuccessfully().and().
        userHasCorrectName("Test User").and().
        userHasValidID()
}
```

### 3. E2E Test Implementation Template
**Use this template for new E2E tests:**

```go
package e2e_test

import (
    "testing"
    "github.com/stretchr/testify/require"
)

type parts struct {
    *testing.T
    require     *require.Assertions
    // Add test-specific fields
    userID      string
    response    *http.Response
    httpClient  *http.Client
}

func newParts(t *testing.T) (*parts, *parts, *parts) {
    t.Helper()

    parts := &parts{
        T:        t,
        require:  require.New(t),
        // Initialize test-specific fields
    }

    parts.setupTestEnvironment()
    return parts, parts, parts
}

// Fluent helper methods
func (p *parts) and() *parts {
    return p
}

func (p *parts) setupTestEnvironment() *parts {
    // Implementation
    return p
}

// Given section methods
func (p *parts) initializeUserService() *parts {
    // Implementation
    return p
}

// When section methods
func (p *parts) createUserWithDetails(details map[string]string) *parts {
    // Implementation
    return p
}

// Then section methods
func (p *parts) userCreatedSuccessfully() *parts {
    // Implementation
    return p
}

// Test implementation
func TestUserService_CompleteUserCreation(t *testing.T) {
    given, when, then := newParts(t)

    given.
        initializeUserService()

    when.
        createUserWithDetails(map[string]string{
            "name":  "John Doe",
            "email": "john@example.com",
        })

    then.
        userCreatedSuccessfully().and().
        userExistsInDatabase().and().
        userHasCorrectDetails()
}
```

## Test Environment Management (ENHANCED)

### CI-Aware Test Configuration
**Automatically adapt test behavior based on execution environment:**

```go
func newChecks() *checks {
    // Default values for local development
    interval := 500 * time.Millisecond
    timeout := 20 * time.Second

    // Use longer intervals for CI environments
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
```

### Environment-Specific Test Behavior
**Gracefully handle different execution environments:**

```go
func (p *parts) cleanupDatabase() {
    if p.db == nil {
        p.Log("Warning: database connection is nil, skipping cleanup")
        return
    }

    queries := []string{
        "DELETE FROM crab.assets",
        "DELETE FROM crab.transcodings",
        "DELETE FROM crab.videos",
    }

    for _, query := range queries {
        _, err := p.db.Exec(query)
        if err != nil {
            p.Logf("Warning: failed to cleanup table with query '%s': %v", query, err)
        }
    }
}

func (p *parts) cleanupSQSQueue() {
    if p.sqsClient == nil {
        p.Log("Warning: SQS client is nil, skipping SQS cleanup")
        return
    }

    queueUrl, err := url.JoinPath(p.sqsConfig.QueueUrl, p.sqsConfig.QueueName)
    if err != nil {
        p.Logf("Warning: failed to build queue URL for cleanup: %v", err)
        return
    }

    _, err = p.sqsClient.PurgeQueue(p.ctx, &awssqs.PurgeQueueInput{
        QueueUrl: aws.String(queueUrl),
    })
    if err != nil {
        p.Logf("Warning: failed to purge SQS queue: %v", err)
    }
}
```

### Test Asset Management
**Organize test files and assets cleanly:**

```
test/
├── e2e/
│   ├── assets/           # Test data files (videos, images, etc.)
│   │   └── test-video.mp4
│   ├── templates/        # Template files for test data generation
│   │   ├── asset_event.json
│   │   └── encode_task_event.json
│   ├── .env.test        # Test environment configuration
│   ├── docker-compose.test.yml
│   ├── e2e_test.go      # Main test scenarios
│   ├── e2e_parts_test.go # Test helpers and fluent interface
│   └── e2e_checks_test.go # Asynchronous check implementation
└── integration/
    └── ...
```

### Configuration Management
**Clean separation of test configurations:**

```go
// .env.test
TEST_DB_URL=postgres://test:test@localhost:5433/testdb
TEST_SQS_QUEUE_URL=http://localhost:4566/000000000000/test-queue
TEST_SERVICE_ADDRESS=http://localhost:18082

// Test setup with environment loading
func newParts(t *testing.T) (*parts, *parts, *parts) {
    t.Helper()
    var envs config.Environment

    // Load test-specific environment
    err := godotenv.Load(".env.test")
    assert.NoError(t, err, "load test config")

    err = env.Parse(&envs)
    assert.NoError(t, err, "parse test config")

    // Continue with test setup...
}
```

## Test Readability and Maintainability (ENHANCED)

### Clean Test Structure Principles
**Based on TVN-cue-crab reference implementation - prioritize readability and maintainability:**

#### 1. Fluent Interface Pattern
**Use method chaining for readable test workflows:**

```go
// Retrieval is under test; upload in given is setup only.
func TestVideoUploadAndRetrieval(t *testing.T) {
    given, when, then := newParts(t)

    given.
        videoFilePath("./assets/test-video.mp4").and().
        uploadVideoFile("E2E Test Video")

    when.
        getVideoByID(given.videoID)

    then.
        videoFoundSuccessfully()
}

// Event processing under test; upload and fetch in given are setup only.
func TestAssetEventProcessing(t *testing.T) {
    given, when, then := newParts(t)

    given.
        videoFilePath("./assets/test-video.mp4").and().
        uploadVideoFile("Asset Event E2E Test Video").and().
        getVideoByID(given.videoID)

    when.
        sendAssetEvent("ACTIVATE", given.videoID)

    then.
        messageSentSuccessfully().and().
        videoHasStatus("ready").and().
        videoHasAssets(2).and().
        noError()
}
```

#### 2. Given/When/Then Structure Enforcement
**ALL tests must follow the Given/When/Then pattern:**

```go
func TestEndpointHealth(t *testing.T) {
    _, when, then := newParts(t)

    when.
        checkHealth()

    then.
        responseCodeIs(200)
}

// Tests with setup (given) use all three parts
func TestComplexWorkflow(t *testing.T) {
    given, when, then := newParts(t)

    given.
        setupTestData().and().
        configureServices()

    when.
        executeWorkflow()

    then.
        verifyExpectedResult().and().
        noError()
}
```

#### 3. Self-Documenting Test Methods
**Method names should clearly describe their purpose:**

```go
// ✅ Clear, descriptive method names
func (p *parts) videoUploadedSuccessfully() *parts
func (p *parts) videoHasStatus(expectedStatus string) *parts
func (p *parts) sendAssetEvent(eventType, videoID string) *parts
func (p *parts) messageSentSuccessfully() *parts

// ❌ Vague or unclear method names
func (p *parts) checkVideo() *parts
func (p *parts) doEvent() *parts
func (p *parts) verify() *parts
```

#### 4. Graceful Error Handling
**Provide meaningful error messages and handle failures gracefully:**

```go
func (p *parts) cleanupDatabase() {
    if p.db == nil {
        p.Log("Warning: database connection is nil, skipping cleanup")
        return
    }

    queries := []string{
        "DELETE FROM crab.assets",
        "DELETE FROM crab.transcodings",
        "DELETE FROM crab.videos",
    }

    for _, query := range queries {
        _, err := p.db.Exec(query)
        if err != nil {
            p.Logf("Warning: failed to cleanup table with query '%s': %v", query, err)
        }
    }
}

func (p *parts) videoHasStatus(expectedStatus string) *parts {
    p.checks.add(func() error {
        resp, err := p.httpClient.Get("http://" + p.envs.ServiceAddress + "/videos/" + p.videoID)
        if err != nil {
            return fmt.Errorf("get video by ID request: %w", err)
        }
        defer resp.Body.Close()

        // ... validation logic with detailed error messages
        if videoResp.Status != expectedStatus {
            return fmt.Errorf("expected status %s, got %s", expectedStatus, videoResp.Status)
        }

        return nil
    })
    return p
}
```

#### 5. Test Data Management
**Organize test data cleanly with templates and fixtures:**

```go
// Template-based test data generation
func (p *parts) sendAssetEvent(eventType, videoID string) *parts {
    eventTime := time.Now().Add(1 * time.Second).Format(time.RFC3339)
    return p.sendMessageFromTemplate("asset_event.json", map[string]any{
        "Type":          eventType,
        "TenantUUID":    "test-tenant-uuid",
        "ExternalUUID":  videoID,
        "Name":          "E2E Test Video",
        "Active":        true,
        "Since":         eventTime,
        "TechnicalTags": "",
    })
}

// Template file: templates/asset_event.json
{
    "Type": "{{.Type}}",
    "TenantUUID": "{{.TenantUUID}}",
    "ExternalUUID": "{{.ExternalUUID}}",
    "Name": "{{.Name}}",
    "Active": {{.Active}},
    "Since": "{{.Since}}",
    "TechnicalTags": "{{.TechnicalTags}}"
}
```

#### 6. Asynchronous Testing Patterns
**Handle eventual consistency with robust retry logic:**

```go
// CI-aware retry configuration
func newChecks() *checks {
    interval := 500 * time.Millisecond
    timeout := 20 * time.Second

    // Use longer intervals for CI environments
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

// Accumulate checks and execute with retry
func (p *parts) videoHasAssets(expectedCount int) *parts {
    p.checks.add(func() error {
        query := `SELECT COUNT(*) FROM crab.assets WHERE video_id = $1`

        var count int
        err := p.db.QueryRow(query, p.videoID).Scan(&count)
        if err != nil {
            return fmt.Errorf("query assets count: %w", err)
        }

        if count != expectedCount {
            return fmt.Errorf("expected %d assets, got %d", expectedCount, count)
        }

        return nil
    })
    return p
}
```

#### 7. Test Organization Best Practices
**Structure tests for maximum maintainability:**

```
test/
└── e2e/
    ├── .env.test              # Test environment configuration
    ├── docker-compose.test.yml
    ├── e2e_test.go            # Main test scenarios (readable workflows)
    ├── e2e_parts_test.go      # Test helpers and fluent interface
    └── e2e_checks_test.go     # Asynchronous check implementation
```

#### 8. Environment Configuration Management
**Separate test configurations cleanly:**

```go
// Separate test configs with environment-specific behavior
func setupTestEnvironment(t *testing.T) *TestEnvironment {
    t.Helper()

    // Load test-specific config
    err := godotenv.Load(".env.test")
    require.NoError(t, err, "load test environment")

    env := &TestEnvironment{
        DBURL:     os.Getenv("TEST_DB_URL"),
        SQSQueue:  os.Getenv("TEST_SQS_QUEUE_URL"),
        ServiceAddr: os.Getenv("TEST_SERVICE_ADDRESS"),
    }

    return env
}
```

## Test Anti-Patterns to Avoid

### ❌ Anti-Pattern: Complex Test Setup
```go
// BAD: Complex setup mixed with test logic
func TestVideoProcessing(t *testing.T) {
    // 50 lines of complex setup here
    db := setupDatabase(t, "complex-config.sql")
    sqsClient := setupSQS(t)
    s3Client := setupS3(t)
    videoProcessor := NewVideoProcessor(db, sqsClient, s3Client)

    // Test logic buried in setup
    // ... actual test logic
}
```

### ✅ Correct Pattern: Clean Separation
```go
// GOOD: Clean setup separation
func TestVideoProcessing(t *testing.T) {
    given, when, then := newParts(t)

    given.
        setupVideoProcessingEnvironment().and().
        uploadTestVideo()

    when.
        startVideoProcessing()

    then.
        videoProcessedSuccessfully().and().
        assetsCreated()
}

func (p *parts) setupVideoProcessingEnvironment() *parts {
    // All complex setup encapsulated in helper method
    p.db = setupDatabase(p.T, "test-config.sql")
    p.sqsClient = setupSQS(p.T)
    p.s3Client = setupS3(p.T)
    p.videoProcessor = NewVideoProcessor(p.db, p.sqsClient, p.s3Client)
    return p
}
```

## Testing Commands Reference

### E2E Test Execution Commands
```bash
# E2E tests (HTTP-based) with docker-compose.test.yml
just test-e2e-up      # Start docker-compose.test.yml services
just test-e2e-run     # Run `go test ./test/e2e/...` against running services
just test-e2e-down    # Stop docker-compose.test.yml services
just test-e2e         # Complete workflow (up → run → down)

# All tests (unit + integration + e2e + browser)
just test-all

# Pre-commit check (unit tests + lint only - fast)
just check

# IMPORTANT: Browser tests are MANDATORY for frontend features
# HTTP-based E2E tests DO NOT validate frontend functionality
```

### Test Environment Variables
- `TEST_DB_URL` - Database connection string for tests
- `TEST_SQS_QUEUE_URL` - SQS queue URL for async tests
- `TEST_SERVICE_ADDRESS` - Service base URL for HTTP tests
- `CI` - Automatically set in CI environments
- `GITHUB_ACTIONS` - Automatically set in GitHub Actions

### 11. Minimal Comments Rule
**Test source carries near-zero comments. The fluent chain IS the documentation.** Delete: `// PRD-COMMENT:` / requirement-tracker blocks (that context belongs in the PR description), `// Given / // When / // Then` section headers (the chain shows it), `// X was captured before...` / `// suppress unused-var` meta-comments, and anything that paraphrases the next line. Keep only: TODO/FIXME with an issue reference, one-line godoc on exported symbols, `// nolint:` directives. If a test needs a paragraph to be understandable, the fix is better names or a DSL method - not a comment.

```go
// ❌ FORBIDDEN: comment-driven test
// PRD-COMMENT: FR10.1 - Client Core Execution: Single Request
// This test verifies that the client can execute one request...
func TestExecuteFile_SingleRequest(t *testing.T) {
    given, when, then := newParts(t)
    // Given
    given.aClient()
    // When
    when.executeFile()
    // Then
    then.noError()
}

// ✅ CORRECT: names + chain speak for themselves
func TestExecuteFile_SingleRequest(t *testing.T) {
    given, when, then := newParts(t)

    given.
        aRequestFixture("single_request.http").and().
        aClient()

    when.
        executeFile()

    then.
        noError()
}
```

### 12. YAGNI Pass Before Every PR (smallest-change discipline)
**Before opening a PR, delete everything that has no caller.** Migration/refactor work breeds orphaned helpers - grep and remove: DSL methods with zero call sites, struct types whose table tests were split, per-fixture builder functions, unused fixture files, dead `_ = x` lines. A helper "we might need later" is a liability; re-adding it later costs less than maintaining it now. Prove the pass: grep each deleted symbol returns 0 hits, then run the full gate (build/vet/lint/tests).

**Never appease the `unused` linter with reference lists (PR#35 round 3).** `var _ = []any{ (*parts).foo, ... }` blocks in DSL files keep dead methods lint-clean forever - 5 dead DSL methods survived 3 review rounds behind them. Delete the blocks and let `unused` name the dead methods, then delete them. Same for `var _ = time.Time{}`-style "silence unused import" lines: fix the import, not the symptom.

**DSL domain split when one file bloats.** Settled shape after rejected alternatives: ONE flat `parts` struct holds ALL state: core (T, assertions, client, ledger) plus every domain's fields flattened in. every fluent method is `func (p *parts) … *parts`, declared in a `<domain>_parts_test.go` file (pure method group, no struct/ctor of its own). Chains never break because every method returns the same `*parts`, so call-site churn is zero. Do NOT route methods through a composite fixture wrapping base + per-domain state structs (reads as a pointless indirection layer; rejected on sight), and do NOT give each domain its own struct type - per-domain-typed returns break mixed-domain chains, and Go has no self-type to fix that. Never let the base embed domains while domains embed the base: that cycle reads as a structural error, not a pattern. Builders live where their state lives (used by 2+ domains → core file; one domain → its file); one package; behavior unchanged.

**ONE ctor: `newParts(t)` in the base file.** It constructs the whole parts literal and returns `p, p, p`, and every Test func calls it. No per-domain ctors (deleted as ceremony), no partial/delegated construction, or core state stays nil. Other domains' builders are callable from any test file because everything is the same `*parts`. Pair rule: each domain primary is an exact-stem pair `X_test.go` ↔ `X_parts_test.go`; additional feature files inside a domain share the domain parts file. A parts file is a pure method group on `*parts` - a parts file with zero methods is deleted.

**One domain per test FILE.** A `client_<feature>_test.go` pairs with the domain its tests assert in; audit violations by counting which parts-file builders each test file calls, then split feature-homogeneous groups into new files rather than swapping ctors per test. Cross-domain setup builders (server boot, file fixtures) used by many files stay base; assertion builders stay in their domain.

**Migration-history godoc is deleted, not shrunk (PR#35 rounds 2-3).** "The legacy tests never exercised this path... gate-mandated count..." belongs in the PR description / bean PoW, never in code. This includes 1-line shrunk survivors and mid-sentence `//` fragments above Test funcs. Delegate contracts for review rounds must state: comments max 1 line across the ENTIRE diff (DSL files included - workers otherwise read "minimal comments" as scoping only Test funcs), only non-obvious WHY, no `// --- moved from X ---` banners. Census: `awk '/^\/\//{c++;next} {if(c>2) print FILENAME": "c" before "NR; c=0}' *_test.go`.

**Repeated mock-infrastructure in Test bodies = missing DSL given (PR#35 rounds 1-3).** The same handler shape appearing 3+ times (GraphQL JSON encoding, canned routes, echo) becomes an `a*Server` method. Likewise multi-line inline content strings (external-file JSON payloads) become committed fixtures under `test/data/<domain>/` with a `*Fixture` DSL variant - single-line payloads may stay inline. Keep fixture layout canonical: one `test/data/` tree; dissolve stray dirs (test/fixtures/) and grep `*.go *.http *.md` for stale paths in the same batch.

---

**These standards are MANDATORY for all E2E tests. No exceptions.**

## Test-DSL constructors (user rule, mirrored from coding-rules)

ONE base struct `parts` holds ALL DSL state, and there is exactly ONE constructor. `newParts(t)` in the base file constructs the whole parts literal and returns `p, p, p`. No composite/god fixture type, no state split across domain structs, no embedding cycle (base embedding domains was rejected as circular; a wrapping fixture type was rejected as a stupid pattern), and NO per-domain wrapper structs either: a stateless `type <dom>Parts struct { parts }` plus its ctor is ceremony with zero behavior; the user deleted the whole set the same day it shipped. Every `*_parts_test.go` file is a pure method group of `func (p *parts) … *parts` builders; a parts file with zero methods is deleted, not kept for symmetry. Keep ALL builders returning the base `*parts`: promotion keeps mixed-domain chains and `.and()` intact, while self-typed generics (`parts[S]`) break every cross-domain chain link (each link needs one concrete type; a `*parts` receiver cannot soundly return a domain-typed `S`; it would return nil). Scratch-compile the candidate topology in a throwaway module (struct + ctor + one mixed-domain chain) before touching the real corpus, and get the user's sign-off on the probe before mass-applying.

## Redesign pushback (lifecycle)

When the user rejects a delivered structure, the fix deletes the rejected abstraction and returns to the simplest shape, and does not patch the abstraction's naming or wiring. Before restructuring a working fluent DSL at all, inventory what the current shape already guarantees (chain typing, mixed-domain access) and price the churn in chain sites, and reject a redesign that trades one complaint for a thousand-site mechanical diff unless the user explicitly asked for the type model. A green gate never excuses a re-added narration comment: audit the diff for added `//` lines before reporting done.
