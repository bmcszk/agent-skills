# Error Handling

## The Golden Rules

```go
// ALWAYS Use errors.Is and errors.As
if errors.Is(err, ErrUserNotFound) {
    return handleNotFound(ctx, userID)
}

var validationErr *ValidationError
if errors.As(err, &validationErr) {
    return handleValidationError(ctx, validationErr)
}

// NEVER Use Equality Operators
if err == ErrUserNotFound {  // WRONG - breaks with wrapped errors
    return handleNotFound(ctx, userID)
}
```

## Error Wrapping with Context

```go
func (s *UserService) CreateUser(ctx context.Context, req *CreateUserRequest) (*User, error) {
    if err := s.validateUser(req); err != nil {
        return nil, fmt.Errorf("CreateUser: validation failed for %s: %w", req.Email, err)
    }
    
    if err := s.repo.SaveUser(ctx, user); err != nil {
        return nil, fmt.Errorf("CreateUser: failed to save user %s: %w", user.ID, err)
    }
    
    return user, nil
}
```

## Sentinel Errors

```go
var (
    ErrUserNotFound     = errors.New("user not found")
    ErrInvalidEmail     = errors.New("invalid email address")
    ErrPaymentDeclined  = errors.New("payment declined")
)
```

## Multi-Error Handling (Go 1.20+)

```go
func (s *UserService) ValidateAndCreate(ctx context.Context, req *CreateUserRequest) (*User, error) {
    var errs []error
    
    if req.Email == "" {
        errs = append(errs, ErrEmailRequired)
    }
    if req.Name == "" {
        errs = append(errs, ErrNameRequired)
    }
    
    if len(errs) > 0 {
        return nil, errors.Join(errs...)
    }
    
    return s.createUser(ctx, req)
}
```

---

