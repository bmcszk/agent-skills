# Interfaces
## CRITICAL: Inline Interface Definition
# Core Rules

## CRITICAL: Inline Interface Definition

**Interfaces MUST be defined inline, just before the struct/constructor that needs them. NEVER create separate interface files.**

```go
// ❌ BAD: Separate interface file (interfaces.go)
package service

type UserRepository interface {
    GetUser(ctx context.Context, id string) (*User, error)
    SaveUser(ctx context.Context, user *User) error
}

// ❌ BAD: Provider defines interface in their package
package database

type UserRepository interface {
    GetUser(id string) (*User, error)
}

// ✅ GOOD: Interface defined inline, just before the consumer
package service

import "context"

// UserRepository is the interface for user data access.
// Defined here because only UserService needs it.
type UserRepository interface {
    GetUser(ctx context.Context, id string) (*User, error)
    SaveUser(ctx context.Context, user *User) error
}

// UserService depends on UserRepository.
type UserService struct {
    repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
    return &UserService{repo: repo}
}
```

### Why Inline Interfaces?

| Separate File | Inline Definition |
|---------------|-------------------|
| Hard to find dependencies | Interface right next to consumer |
| Unclear ownership | Consumer owns the interface |
| Encourages fat interfaces | Encourages small, focused interfaces |
| Multiple consumers share | Each consumer defines exactly what it needs |

### Rules

1. **NEVER** create files like `interfaces.go`, `types.go` for interfaces
2. **ALWAYS** define interface just before the struct that uses it
3. **ALWAYS** keep interface in same file as the consumer
4. **Consumer defines** the interface, not the provider

---

