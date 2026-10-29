# Fluent Test Design Standards (MANDATORY)

This document provides comprehensive standards for writing fluent E2E tests using the Given/When/Then pattern. All E2E tests MUST follow these exact patterns and rules.

## Given/When/Then phase roles (Extremely important)

Hard rules - fluent **and** classic:

| Phase | Role | Allowed | Forbidden |
|---|---|---|---|
| **given** | Set the stage | Configure state, start deps, seed data - setup **explicit** | Asserts, expects, outcome checks; the action under test |
| **when** | Exercise | Usually **one** fluent call: trigger only what this test covers | Asserts, validation, extra setup unrelated to the trigger |
| **then** | Verify | **All** asserts, expects, outcome checks | Actions under test, new setup |

Naming a method `…Successfully()` does not change the rule: if it asserts,
it is chained only under `then.`, never `given.` or `when.`. In `then.`,
assert the **when** action and its outcomes - not setup already done in
`given.` (e.g. do not call `videoUploadedSuccessfully()` after upload
lives only under `given.`).

## Fluent Test Builder Pattern
**Based on TVN-cue-crab reference implementation - use fluent interfaces for readable test composition:**

```go
package e2e_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

type parts struct {
    *testing.T
    responseCode  int
    responseBody  []byte
    videoID   string
    videoPath string
    checks    *checks
}

func newParts(t *testing.T) (*parts, *parts, *parts) {
    t.Helper()

    parts := &parts{
        T:      t,
        checks: newChecks(),
    }

    // Setup test environment
    parts.setupTestEnvironment()

    return parts, parts, parts  // given, when, then
}

// Fluent chaining methods
func (p *parts) and() *parts {
    return p
}

func (p *parts) videoFilePath(path string) *parts {
    p.videoPath = path
    return p
}

func (p *parts) uploadVideoFile(title string) *parts {
    // Implementation reads p.videoPath
    return p
}

func (p *parts) videoUploadedSuccessfully() *parts {
    assert.Equal(p.T, http.StatusCreated, p.responseCode)
    return p
}

func (p *parts) noError() *parts {
    assert.NoError(p.T, p.checks.repeatRun())
    return p
}
```

### Test Usage Example
**Clean, readable test structure with fluent chaining:**

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

## E2E Test Structure Requirements

**ALL E2E tests MUST follow the exact Given/When/Then structure with these specific patterns:**

```go
func TestWorkflow_CriticalUserAction(t *testing.T) {
    given, when, then := newParts(t)

    given.
        setupTestData().and().
        configureServices()

    when.
        executeCriticalAction()

    then.
        actionSucceeded().and().
        noError()
}
```

## MANDATORY Formatting Rules

### 1. Given/When/Then Section Structure
**Every E2E test MUST use this exact pattern:**

```go
// ✅ CORRECT: Proper Given/When/Then structure
func TestAPI_ResourceCreation(t *testing.T) {
    given, when, then := newParts(t)

    given.
        setupResourceScenario()

    when.
        createResourceViaAPI()

    then.
        resourceCreatedSuccessfully().and().
        responseContainsExpectedData()
}

// ❌ FORBIDDEN: Missing then section
func TestAPI_ResourceCreation(t *testing.T) {
    given, when, _ := newParts(t)

    given.
        setupResourceScenario()

    when.
        createResourceViaAPI().and().
        resourceCreatedSuccessfully()  // WRONG: validation in when section
}

// ❌ FORBIDDEN: Asserts in given
func TestAPI_ResourceCreation(t *testing.T) {
    given, when, then := newParts(t)

    given.
        setupResourceScenario().and().
        resourceCreatedSuccessfully()  // WRONG: assert belongs in then

    when.
        createResourceViaAPI()

    then.
        responseContainsExpectedData()
}
```

### 2. Fluent Method Chaining Format
**ALL fluent chains must follow this exact formatting:**

```go
// ✅ CORRECT: Proper fluent formatting
given.
    setupScenario().and().
    configureServices()

when.
    executeAction()

then.
    verifyResult().and().
    cleanupState()
```

### 3. Method Positioning Rules
**Follow these rules for method chaining:**

```go
// ✅ CORRECT: .and() at end of line, continuation on next line
when.
    executeHTTPRequest("/api/resource")

then.
    validateResponseCode(201)

// ✅ CORRECT: Multiple validations chained
then.
    responseCodeIs(200).and().
    responseContains("success").and().
    noError()

// ❌ FORBIDDEN: validation chained under when
when.
    executeHTTPRequest("/api/resource").and().
    validateResponseCode(201)  // WRONG: validation belongs in then

// ❌ FORBIDDEN: .and() at start of line
when.
    executeHTTPRequest("/api/resource")
        .and().validateResponseCode(201)  // WRONG: .and() mispositioned
```

### 4. Helper Function Usage Rules
**ALL setup operations MUST use fluent methods, NEVER direct helper function calls:**

```go
// ❌ FORBIDDEN: Direct helper function call in test
func TestScenarioFileLoading(t *testing.T) {
    configFile := createTestUnifiedConfigFile(t)  // WRONG: Direct call
    _, when, then := newServerParts(t, configFile)

    when.
        a_get_request_is_made_to("/api/resource")

    then.
        the_response_is_successful()
}

// ❌ FORBIDDEN: Direct config creation with local variable
func TestPerformanceTest(t *testing.T) {
    configFile := createPerformanceTestConfig(t)  // WRONG: Local variable
    when, then := newServerParts(t, configFile)   // WRONG: Passing as parameter

    when.
        a_load_test_is_executed()

    then.
        the_response_time_is_acceptable()
}

// ✅ CORRECT: Use fluent method in given section
func TestScenarioFileLoading(t *testing.T) {
    given, when, then := newParts(t)

    given.
        unifiedConfigFile()  // Fluent method that creates config and stores in parts.configFile

    when.
        a_get_request_is_made_to("/api/resource")

    then.
        the_response_is_successful()
}

// ✅ CORRECT: Config creation via fluent method
func TestPerformanceTest(t *testing.T) {
    given, when, then := newParts(t)

    given.
        performanceTestConfig()  // Creates config, stores in parts.configFile

    when.
        a_load_test_is_executed()  // Accesses parts.configFile internally

    then.
        the_response_time_is_acceptable()
}
```

**Critical Rules:**
- NEVER create config files with direct function calls like `configFile := createXXX(t)`
- NEVER pass config files as parameters to factory functions like `newServerParts(t, configFile)`
- ALWAYS create config files via fluent methods in the `given` section
- ALWAYS store config file paths in `parts.configFile`
- Config creation methods MUST return `*parts` for chaining

**Rationale:**
- Maintains consistent fluent pattern throughout tests
- Improves test readability and maintainability
- Makes test setup explicit and traceable
- Supports method chaining for complex setup scenarios
- Eliminates local variables and parameter passing

### 5. Single Given Chain Rule
**Each test MUST have only ONE given statement that chains all setup steps:**

```go
// ❌ FORBIDDEN: Multiple given statements
func TestComplexSetup(t *testing.T) {
    given, when, then := newParts(t)

    given.setupDatabase()        // WRONG: Separate statements
    given.createTestData()       // WRONG: Separate statements
    given.configureServices()    // WRONG: Separate statements

    when.executeAction()

    then.verifyResult()
}

// ✅ CORRECT: Single given chain
func TestComplexSetup(t *testing.T) {
    given, when, then := newParts(t)

    given.
        setupDatabase().and().
        createTestData().and().
        configureServices()

    when.
        executeAction()

    then.
        verifyResult()
}

// ✅ CORRECT: Single given method (when no chaining needed)
func TestSimpleSetup(t *testing.T) {
    given, when, then := newParts(t)

    given.
        unifiedConfigFile()

    when.
        a_get_request_is_made_to("/api/resource")

    then.
        the_response_is_successful()
}
```

**Rationale:**
- Forces proper fluent chaining pattern
- Ensures all setup methods return `*parts` for chaining
- Makes the setup phase atomic and clear
- Prevents scattered setup statements
- All test state MUST be stored in the `parts` struct

**Critical Rule: All Test State in Parts Struct**
```go
// ❌ FORBIDDEN: Local variables for test state
func TestBadPattern(t *testing.T) {
    given, when, then := newParts(t)

    configFile := createConfigFile(t)  // WRONG: State not in parts
    userID := "123"                    // WRONG: State not in parts

    given.setupWithConfig(configFile)  // Passing state as parameter
    when.createUser(userID)
    then.verifyUser(userID)
}

// ✅ CORRECT: All state in parts struct
type parts struct {
    *testing.T
    require    *require.Assertions
    configFile string  // State stored in parts
    userID     string  // State stored in parts
    response   *http.Response
}

func (p *parts) unifiedConfigFile() *parts {
    // Create config and store in parts
    p.configFile = createAndStoreConfig(p.T)
    p.setupScenarioTestServer(p.configFile)
    return p
}

func (p *parts) createUserWithID(id string) *parts {
    p.userID = id  // Store state in parts
    // ... create user logic
    return p
}

func TestCorrectPattern(t *testing.T) {
    given, when, then := newParts(t)

    given.
        unifiedConfigFile()  // Config stored in parts.configFile

    when.
        createUserWithID("123")  // ID stored in parts.userID

    then.
        verifyUserCreated()  // Accesses parts.userID internally
}
```

**Why This Matters:**
- Enables method chaining without parameter passing
- Makes test state accessible across given/when/then phases
- Supports cleanup and assertions that need access to setup data
- Prevents test state from being scattered across local variables

## Variable Declaration Rules

### 1. Section Variable Declaration
**Declare variables based on what sections are actually used:**

```go
// ✅ CORRECT: Only declare variables that are used
func TestWithGivenAndWhen(t *testing.T) {
    given, when, then := newParts(t)
    // Uses all three sections
}

func TestWithWhenAndThen(t *testing.T) {
    _, when, then := newParts(t)
    // No setup needed
}

func TestWithWhenOnly(t *testing.T) {
    _, when, _ := newParts(t)
    // Simple test with no verification
}
```

### 2. Unused Variable Elimination
**NEVER declare unused variables:**

```go
// ❌ FORBIDDEN: Unused given variable
func TestSimpleAction(t *testing.T) {
    given, when, then := newParts(t)  // given is unused
    when.
        executeAction()
    then.
        verifyResult()
}

// ✅ CORRECT: Only declare what's needed
func TestSimpleAction(t *testing.T) {
    _, when, then := newParts(t)
    when.
        executeAction()
    then.
        verifyResult()
}
```

## Response Handling Patterns

### 1. Response Storage Pattern
**Store responses in the parts struct for better readability:**

```go
// ✅ CORRECT: Store responses in parts struct
func (p *parts) executeHTTPRequest(endpoint string) *parts {
    responses, err := p.httpClient.Get(endpoint)
    p.require.NoError(err, "Failed to execute HTTP request")
    p.responses = make([]any, len(responses))
    for i, resp := range responses {
        p.responses[i] = resp
    }
    return p
}

func (p *parts) validateResponse() *parts {
    // Access stored responses from parts struct
    resp := p.responses[0].(*http.Response)
    p.require.Equal(200, resp.StatusCode)
    return p
}
```

### 2. Method Return Value Pattern
**Fluent methods should return *parts for chaining:**

```go
// ✅ CORRECT: Methods support fluent chaining
func (p *parts) createResource() *parts {
    // Implementation
    return p
}

// ✅ CORRECT: Usage in fluent chain
when.
    createResource().and().
    verifyResource()
```

## E2E Test Quality Standards

### 1. Test Completeness Requirements
**Every E2E test must cover:**
- ✅ Setup phase (given)
- ✅ Action phase (when)
- ✅ Verification phase (then)
- ✅ Cleanup (if needed)
- ✅ Error handling validation

### 2. Readability Standards
**Tests must be self-documenting:**
- ✅ Clear test names: `TestComponent_Action_ExpectedResult`
- ✅ Descriptive method names
- ✅ Proper section comments
- ✅ Meaningful assertion messages

### 3. Maintainability Requirements
**Tests must be maintainable:**
- ✅ Reusable helper methods
- ✅ Clear separation of concerns
- ✅ Consistent error handling
- ✅ Environment-independent execution

## Anti-Patterns to Avoid

### ❌ Structural Anti-Patterns
```go
// FORBIDDEN: Missing then section
func TestBad(t *testing.T) {
    given, when, _ := newParts(t)
    when.executeAction()  // No verification
}

// FORBIDDEN: Validation in wrong section
func TestBad(t *testing.T) {
    given, when, then := newParts(t)
    when.executeAction().and().verifyResult()  // Wrong section
}

// FORBIDDEN: Unused variables
func TestBad(t *testing.T) {
    given, when, then := newParts(t)  // given, then unused
    when.executeAction()
    then.verifyResult()
}
```

### ❌ Formatting Anti-Patterns
```go
// FORBIDDEN: Inconsistent chaining
when.
    method1().
        method2()  // Missing .and().
    then.verify()

// FORBIDDEN: Misplaced .and()
when.
    method1().
        .and().method2()  // Wrong indentation

// FORBIDDEN: Long single-line chains
when.method1().and().method2().and().method3().and().method4()  // Too long
```

## Advanced Patterns

### Asynchronous Check Pattern
**Robust pattern for testing eventual consistency with retry logic:**

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
    // CI-aware defaults
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

// Usage in test methods
func (p *parts) videoHasStatus(expectedStatus string) *parts {
    p.checks.add(func() error {
        resp, err := p.httpClient.Get("http://" + p.envs.ServiceAddress + "/videos/" + p.videoID)
        if err != nil {
            return fmt.Errorf("get video by ID request: %w", err)
        }
        defer resp.Body.Close()

        // Parse and validate status
        var videoResp struct { Status string `json:"status"` }
        if err := json.NewDecoder(resp.Body).Decode(&videoResp); err != nil {
            return fmt.Errorf("parse video response: %w", err)
        }

        if videoResp.Status != expectedStatus {
            return fmt.Errorf("expected status %s, got %s", expectedStatus, videoResp.Status)
        }

        return nil
    })
    return p
}
```

### Template-Based Test Data Pattern
**Clean approach for managing complex test data with templates:**

```go
// Template files in templates/ directory
// templates/asset_event.json
{
    "Type": "{{.Type}}",
    "TenantUUID": "{{.TenantUUID}}",
    "ExternalUUID": "{{.ExternalUUID}}",
    "Name": "{{.Name}}",
    "Active": {{.Active}},
    "Since": "{{.Since}}",
    "TechnicalTags": "{{.TechnicalTags}}"
}

// Test method using templates
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

func (p *parts) sendMessageFromTemplate(templateFile string, data map[string]any) *parts {
    tmpl, err := template.ParseFiles(filepath.Join("templates", templateFile))
    assert.NoError(p.T, err, "parse template file")

    var buf bytes.Buffer
    err = tmpl.Execute(&buf, data)
    assert.NoError(p.T, err, "execute template")

    return p.sendSQSMessage(buf.String())
}
```

### 6. t.Run Promotion Rule
**Prefer separate top-level Test funcs over t.Run subtests.** Only use t.Run when a subtest genuinely needs state isolation (fresh parts, fresh server, fresh env). t.Run that exists only to share a "name with a twist" is an anti-pattern - split into separate Test funcs with descriptive names.

```go
// ❌ FORBIDDEN: t.Run wrapper only to share a name
func TestCookieJarHandling(t *testing.T) {
    t.Run("default_behavior", func(t *testing.T) {
        given, when, then := newParts(t)
        // ...
    })
    t.Run("directive_no_cookie_jar", func(t *testing.T) {
        given, when, then := newParts(t)
        // ...
    })
}

// ✅ CORRECT: two top-level Test funcs, one per scenario
func TestCookieJarHandling_DefaultBehavior(t *testing.T) {
    given, when, then := newParts(t)
    // ...
}

func TestCookieJarHandling_NoCookieJarDirective(t *testing.T) {
    given, when, then := newParts(t)
    // ...
}
```

**Rationale:**
- Simpler test func bodies; complexity stays in the DSL
- `go test -run TestCookieJarHandling_NoCookieJarDirective` works for targeted runs
- No wrapper Test funcs - every test is directly runnable
- Junit reports one clean entry per test

### 7. Fixtures Over Inline Strings
**aHttpFile(content) accepts SHORT inline HTTP requests only.** For multi-line request bodies with JSON templates, multi-line bodies with @vars, or `<@` / `<` external-file references, commit a fixture in `test/data/` and use `aHttpFileFromTemplate(name)`. Tests must not encode request bodies with sprintf + newlines + escapes.

```go
// ❌ FORBIDDEN: inline sprintf'd .http body
anExternalFile("test_vars.json", `...long inline JSON...`).and().
aHttpFile(fmt.Sprintf(`@userId = user123
POST %s/post
<@ ./test_vars.json`, given.serverURL))

// ✅ CORRECT: committed fixture + one DSL call
anExternalFile("test_vars.json", `...`).and().
aHttpFileFromTemplate("external_file_with_vars.http")
```

**Rationale:**
- Fixture files diff cleanly and are reviewable
- No escaping pitfalls in Go raw strings
- Template variables ([[.ServerURL]]) keep the server URL dynamic

### 8. Handler Assertions via DSL
**aHttpServer's handler must NOT contain inline `if r.Method != X { t.Errorf(...) }` cascades.** Keep the handler short (echo back / 200 OK). Assertions belong in the then-chain via `serverReceivedMethodAndPath` / `serverReceivedHeader*` / `serverReceivedBody*` / `serverReceivedJSONBody` reading capturedRequests.

```go
// ❌ FORBIDDEN: handler with inline t.Errorf cascade
aHttpServer(func(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        t.Errorf("method = %v", r.Method)
    }
    if got := r.Header.Get("Content-Type"); got != "application/json" {
        t.Errorf("Content-Type = %q", got)
    }
    // ...
})

// ✅ CORRECT: short echo handler + DSL assertions in then
aJsonEchoServer().and().
    // ... other given

then.
    serverReceivedMethodAndPath(0, http.MethodPost, "/post").and().
    serverReceivedHeaderValue(0, "Content-Type", "application/json").and().
    serverReceivedBodyParsesAsJSON(0)
```

**Rationale:**
- Handler stays a plain test-data function (no *testing.T dependency)
- Assertion failures report through the fluent chain, not buried t.Errorf
- Captured requests can be asserted multiple ways without re-serving

### 9. Faker/Rule Data Structures Belong in DSL
**When a test needs a list of validation rules (key, pattern, fieldCount, containsCheck), expose ONE DSL method taking a small struct slice - not per-fixture helper functions that build the slice from a separate file.**

```go
// ❌ FORBIDDEN: per-fixture rule builders in the test file
func fakerPersonDataHeaders() (vsCode, jetBrains []fakerHeaderRule) { /* ... */ }
func fakerContactInternetHeaders() (vsCode, jetBrains []fakerHeaderRule) { /* ... */ }

// Test:
vsCode, jetBrains := fakerPersonDataHeaders()
then.
    assertFakerHeaders(0, vsCode).and().
    assertFakerHeaders(1, jetBrains)

// ✅ CORRECT: one DSL method + inline rule literal
then.
    serverReceivedFakerHeaders(0, []fakerHeaderRule{
        {key: "X-Random-First-Name", pattern: `^\S+$`, fieldCount: 1},
        {key: "X-Random-Job-Title", pattern: `^.+$`, fieldCount: -1},
        {key: "X-User-Agent", containsCheck: "Mozilla"},
    }).and().
    serverReceivedFakerHeaders(1, []fakerHeaderRule{ /* ... */ })
```

**Rationale:**
- Rules visible inline next to the test that owns them
- No indirection through builder functions
- One DSL entry point; rule types shared across faker tests

## Test Helper Functions
**ONLY helper functions MUST use `t.Helper()` (NOT test functions).** All helpers should follow Given/When/Then structure:

```go
func setupTestData(t *testing.T) TestData {
    t.Helper()

    data := TestData{
        Field1: "value1",
        Field2: "value2",
    }

    return data
}

// Enhanced fluent helper
func (p *parts) cleanupDatabase() *parts {
    if p.db == nil {
        p.Log("Warning: database connection is nil, skipping cleanup")
        return p
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

    return p
}
```

---
