# Fluent stage tests

Shared pattern for integration and E2E tests.

## File pairs

Integration and E2E tests always come in pairs:

- `*_test.go`, scenario functions only
- `*_stage_test.go`, `stage` struct, `newStage`, and all fluent methods

Do not put scenario tests and stage helpers in the same file.

## Structure

- Tests use `given, when, then := newStage(t)`.
- The shared state type is named `stage`.
- `newStage(t)` returns `(*stage, *stage, *stage)`.
- `func (s *stage) and() *stage { return s }`.
- All mutable test state lives on `stage`. IDs, payloads, stats, captured responses, and any other shared data.
- Scenario files contain scenarios only.
- The `stage` struct and fluent methods live in a separate `*_stage_test.go` file.
- Declare only the phases a test uses. A test with no setup is `_, when, then := newStage(t)`. Never leave an unused variable.
- Every test has a `when` and a `then`. A test with no `then` proves nothing.

## Given / when / then roles

Do not blur phases. Each block has one job. Polluting a phase (assert in `when`, act under test in `given`, setup in `then`) is wrong even when the test still passes.

| Phase | Responsibility | Method naming |
|-------|----------------|---------------|
| **given** | Set the stage: configure initial state, start dependencies, prepare test data on `stage`. Every setup step is explicit in the scenario or in a `given` method it calls. No hidden or implicit arrange. | `a*` prefix, for example `anOrderWithTwoItems()`, `aDryRunOrder()` |
| **when** | Trigger only the action under test, usually one fluent call (one-liner). | present participle `-ing`, for example `creatingOrder()`, `gettingOrder()` |
| **then** | All assertions, expects, and outcome checks. Nothing else. | state/check, for example `noError()`, `statusIs()`, `errorMessageContains()` |

Rules:

- **given**: explicit setup and preconditions only. Never assert. Never perform the action under test (the HTTP call or workflow this test proves; readiness, health, and wait helpers such as `orderAPIIsReady()` are setup and belong here). Never leave arrange off `stage` or outside visible `given` methods.
- **when**: usually a single method call, the one act this test exercises. Never assert. Never build request bodies here (set `requestBody` and other arrange in `given`). Never stack unrelated actions. Split into separate tests.
- **then**: every `require.*`, `assert.*`, and outcome verification lives here. Never trigger actions or new setup. Assert the `when` action and its outcome, not setup that `given` already established.
- A method named `...Successfully()` that asserts is still an assert. Chain it only under `then`.
- Ideally each test has exactly one `given`, one `when`, and one `then` block. The `when` action is what the test function is testing.
- Do not repeat `given` / `when` / `then` blocks in one test. Split multi-step workflows into separate tests, or move prerequisite setup into `given` stage methods.
- Chain `given` steps with `.and()` when data setup is needed after readiness checks.
- Put `.and()` at the end of the line. Start the next call on the next line. Do not put long chains on one line.
- Do not use local variables for shared test state. Store everything on `stage`.
- Do not call setup helpers directly from scenarios; wrap them in fluent stage methods. Do not pass config or fixtures as constructor parameters; a `given` method creates them and stores them on `stage`.
- Do not call low-level helpers like `postJSON(...)` from scenario files. Use behaviour-named `when` methods like `creatingOrder()`.
- Move complex setup (several clients, seeded data) into one `given` method. Do not inline it in the test body.

### Good example

One `given` / `when` / `then`. Behaviour language throughout. No local variables.

```go
func TestOrderAPIIntegration_CreateOrderRejectsInvalidJSON(t *testing.T) {
    given, when, then := newStage(t)

    given.
        orderAPIIsReady().and().
        anOrderWithInvalidJSON()

    when.
        creatingOrder()

    then.
        noError().and().
        statusIs(http.StatusBadRequest).and().
        errorMessageContains("valid JSON")
}
```

Read-only cases need only readiness in `given`:

```go
given.
    orderAPIIsReady()

when.
    listingOrders()
```

A test with no setup skips `given`:

```go
_, when, then := newStage(t)

when.
    gettingLiveEndpoint()

then.
    statusIs(http.StatusOK)
```

### Bad example

Multiple `given` / `when` / `then` blocks, local variables, and low-level HTTP calls in the scenario.

```go
func TestOrderAPIIntegration_CancelPublishesUpdatedEventWithReason(t *testing.T) {
    given, when, then := newStage(t)
    orderID := uuid.NewString()                     // bad: local variable
    stats := storage.OrderStats{Items: 2}           // bad: local variable

    given.
        ensureEventStream().and().
        orderAPIIsReady()

    when.
        postJSON("/v1/orders", orderWithItems(orderID)) // bad: not behaviour language
    then.
        statusIs(http.StatusCreated)

    given. // bad: second given/when/then block
        aDraftOrderWithID(orderID)
    when.
        creatingOrderFromDraft(orderID)
    then.
        statusIs(http.StatusCreated)

    when. // bad: third when/then block
        cancellingOrder(orderID, "out of stock", stats)
    then.
        cancellationSucceeded()
}
```

Fix by splitting into separate tests (one `when` each) and moving IDs, stats, and payloads onto `stage` via `a*` methods.

## Scenario files

- One `Test*` function per case. Name it `TestSubject_Scenario_Outcome`.
- Do not use table-driven `tests := []struct{...}` in scenario files.
- Do not wrap cases in `t.Run`. Use a `t.Run` subtest only when it needs isolation a top-level test cannot give (fresh stage, fresh server). Separate `Test*` functions run alone with `go test -run` and give one report entry each.
- Do not use generic `perform(act)` helpers.
- Do not pass raw JSON, paths, or IDs in scenario files.
- Reuse one generic `when` method per endpoint; vary only `given` data setup.

## Stage state

Store mutable request/response state on `stage`, not in method parameters or package-level helpers.

Typical HTTP stage fields:

```go
type stage struct {
    *testing.T
    require            *require.Assertions
    baseURL            string
    httpClient         *http.Client
    requestBody        string
    responseStatusCode int
    responseRaw        []byte
    responseErr        error
    checks             *checks
}
```

- `given` methods with `a*` prefix set `requestBody` (and other arrange state).
- `when` methods call `do()` which reads `requestBody` and populates response fields.
- `then` methods assert against response fields.

## HTTP actions

- Use one generic `when` method per endpoint, not one method per test case.
- Good: `creatingOrder()` reused across all create-order scenarios.
- Avoid: `createOrderWithoutItems()` that both builds the body and sends the request.

Capture transport errors on `stage` and assert them in `then`:

```go
func (s *stage) do(method, path string) *stage {
    // ...
    if err != nil {
        s.responseErr = err
        return s
    }
    // ...
}

func (s *stage) noError() *stage {
    s.require.NoError(s.responseErr)
    return s
}
```

Do not `require.NoError` inside `do()` for transport failures. Keep "could not reach the service" separate from "service returned 400".

## Resource cleanup

- Every method that reads a response body closes it: check the transport error first, then `defer resp.Body.Close()`. This includes async `then` checks — each poll opens a new body, so each poll must close one.
- Tear down what `given` sets up. Compose projects, containers, temp dirs, and listeners get a deferred cleanup (registered in `newStage` or in the method that started the resource), not a hope that the CI runner garbage-collects them. A failing cleanup logs a warning and moves on; it never panics the test.

## Naming

| Kind | Pattern | Examples |
|------|---------|----------|
| Arrange / data | `a` + noun phrase | `anOrderWithTwoItems()`, `anOrderWithoutCustomer()` |
| Act / HTTP | verb-ing + target | `creatingOrder()`, `gettingLiveEndpoint()`, `listingOrders()` |
| Assert | state or check | `noError()`, `statusIs()`, `routeIsRegistered()`, `errorMessageContains()` |
| Internal builders | `a` + type + `With` | `anOrderWithAttributes()`, `anOrderWithStatus()` |

Names describe behaviour. `checkOrder()`, `doEvent()`, and `verify()` say nothing; `orderHasStatus("shipped")` does.

Payload builders are `stage` methods that return `*stage`, not package-level functions returning `string`.

## Phase markers

Do not write `// given`, `// when`, `// then` comments in fluent tests. The `given.`, `when.`, and `then.` receivers already mark the phases. A test doc comment names only a contract the test name does not carry, never the chain below it. The unit tests are the exception: they have no receivers, so they keep the markers.

## Chains

- Use one `given` chain, one `when` action, and one `then` chain per test.
- The `when` method names the behaviour under test.
- Respect the phase boundaries above: `given` is explicit setup, `when` is the act under test (usually one call), `then` holds all asserts.
- Start `then` with `noError()` when the scenario sends HTTP requests.
- If a workflow needs multiple actions, write separate tests, one per `when`, not multiple `given` / `when` / `then` blocks in one function.

```go
func TestWorkflow(t *testing.T) {
    given, when, then := newStage(t)

    given.
        serviceIsReady().and().
        aValidRequest()

    when.
        sendingRequest()

    then.
        noError().and().
        statusIs(http.StatusOK).and().
        bodyContains("expected")
}
```

More on stage layout, large stages, and chain typing: [stage-structure.md](stage-structure.md). Test data, fake servers, async checks: [test-data-and-config.md](test-data-and-config.md).
