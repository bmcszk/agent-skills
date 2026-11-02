# Formatting Rules (MANDATORY)

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

