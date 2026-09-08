---
name: go-unit-tests
description: 'Go unit testing best practices with testify, mocking patterns, and Given/When/Then structure. Use when writing unit tests, creating mock implementations, or testing business logic via public APIs. Enforces blackbox testing with external test packages (_test). Keywords: unit testing, go test, testify, mocking, table-driven tests, blackbox testing, given when then.'
license: MIT
metadata:
  audience: developers
  workflow: testing
  category: unit-testing
  technologies: go, testify, mocking
---

## What I do

Blackbox unit testing with mocks and Given/When/Then structure.

## When to use me

- Writing unit tests
- Creating mock implementations
- Testing business logic via public APIs

## Rules

### Blackbox Testing (CRITICAL)

Unit tests MUST be blackbox tests:
- **Package**: `package <name>_test` (e.g., `package handlers_test`)
- **Scope**: Test ONLY public functions/methods
- **Never**: Access unexported fields or private functions

```go
// ✅ CORRECT: Test public method from external test package
package handlers_test

func TestHandler_PublicMethod(t *testing.T) {
    // given
    mockDep := &MockDependency{}
    handler := handlers.NewHandler(mockDep) // Public constructor
    
    // when
    result, err := handler.PublicMethod() // Public method
    
    // then
    assert.NoError(t, err)
}
```

### Test Structure

```go
func TestService_CreateUser(t *testing.T) {
    // given
    mockRepo := &MockRepository{}
    mockRepo.On("Save", mock.Anything, mock.Anything).Return(nil)
    service := service.NewService(mockRepo)
    
    // when
    err := service.CreateUser("test@example.com", "Test User")
    
    // then
    assert.NoError(t, err)
    mockRepo.AssertExpectations(t)
}
```

### Dependency Injection

```go
// ❌ Anti-Pattern: External dependencies
func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    resp, _ := http.Get(h.backendURL) // BAD: Real HTTP call
}

// ✅ Correct: Dependency injection
type HTTPClient interface {
    Get(url string) (*http.Response, error)
}

type Handler struct {
    client HTTPClient
}
```

### Mock Pattern

```go
type MockRepository struct {
    mock.Mock
}

func (m *MockRepository) GetUser(ctx context.Context, id string) (*User, error) {
    args := m.Called(ctx, id)
    if user := args.Get(0); user != nil {
        return user.(*User), args.Error(1)
    }
    return nil, args.Error(1)
}
```

## Standards

- **Speed**: <10ms per test
- **Isolation**: No external dependencies
- **Naming**: `TestComponent_Scenario_ExpectedResult`

## Commands

```bash
# Use project's test runner (make or just)
<runner> test-unit    # Unit tests only
<runner> check        # vet + test + lint
```

## Forbidden

- NEVER test private functions/fields (whitebox testing)
- NEVER use `wantErr bool` - split into separate tests
- NEVER access unexported members
- NEVER use build tags
- NEVER use `//nolint` comments
- NEVER delete or skip tests
