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
