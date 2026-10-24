# Performance & Footguns

## Go embedding (general rule, not DSL-specific)
Embedding promotes the embedded struct's members onto the outer type. NEVER re-bind the host inside a method (`p := c.parts` is always wrong) - call promoted members on the receiver directly (`c.require`, `c.parsedFile`, `c.aClient()`). A receiver hop is justified ONLY when passing the host as a value to another function. Never build a bidirectional embedding cycle (base embeds sub-structs while sub-structs embed the base): promotion through a cycle compiles but reads as a structural error; shape it one-way (composite embeds state structs, state structs hold fields only).

Before a receiver-wide rewrite, verify the moved binding is value-only:
scan each body for `p` used WITHOUT a following dot (`[^[\w.]p\b(?!\s*\.)]`) - a value usage (passed as an argument) needs the binding kept; dot-only
usages rewrite mechanically to receiver refs and `go vet` catches the rest.

## Marker structs need real state or the unused linter kills them
An empty domain struct added only to satisfy a layout rule (`type envParts
struct{}`) fails `unused` unless something references it. Give it its natural
domain state (the fields its builders write) and embed it in the composite - then the linter passes because real code reads and writes the fields, not
because a silence block hid the type.

## No lint-appeasement constructs
`var _ = []any{ Type{} }` compile-assert blocks (and `var _ = time.Time{}`-style unused-import silencers) are dead noise: type safety is already proven by every method using the type. Delete the block and fix the import, not the symptom - the `unused` linter then names genuinely dead symbols for deletion instead of hiding them.

# Performance

## Pre-allocate with Capacity

```go
// BAD: Multiple reallocations
items := []int{}
for i := 0; i < 1000; i++ {
    items = append(items, i)
}

// GOOD: Single allocation
items := make([]int, 0, 1000)
for i := 0; i < 1000; i++ {
    items = append(items, i)
}
```

## Sync Primitives

```go
// Mutex for protecting shared state
type Counter struct {
    mu    sync.Mutex
    count int
}

func (c *Counter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

// RWMutex for read-heavy workloads
type Cache struct {
    mu    sync.RWMutex
    items map[string]string
}

func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    val, ok := c.items[key]
    return val, ok
}
```

## sync.Once for Initialization

```go
type Service struct {
    once   sync.Once
    config *Config
}

func (s *Service) getConfig() *Config {
    s.once.Do(func() {
        s.config = loadConfig()
    })
    return s.config
}
```

---

# Go Footguns

## Loop Variable Capture

```go
// BAD: All goroutines see last value
for _, v := range values {
    go func() {
        fmt.Println(v) // WRONG
    }()
}

// GOOD: Capture loop variable
for _, v := range values {
    v := v // Create new variable
    go func() {
        fmt.Println(v)
    }()
}
```

## Interface Nil Gotcha

```go
var err error       // err == nil
var e *MyError      // e == nil
err = e             // err != nil! (interface has type info)

// Check properly
if err != nil {
    // Handle error
}
```

## Slice Memory Leak

```go
// BAD: Keeps reference to entire array
func firstTwo(data []int) []int {
    return data[:2]
}

// GOOD: Copy to avoid memory leak
func firstTwo(data []int) []int {
    result := make([]int, 2)
    copy(result, data[:2])
    return result
}
```

## Map Concurrency

```go
// BAD: Concurrent map access
var m = make(map[string]int)
go func() { m["key"] = 1 }()
go func() { _ = m["key"] }() // panic!

// GOOD: Use sync.RWMutex or sync.Map
var mu sync.RWMutex
mu.Lock()
m["key"] = 1
mu.Unlock()
```

---

# Naming Conventions

| Element | Convention | Example | Anti-Pattern |
|---------|------------|---------|--------------|
| Package | Short, lowercase | `user`, `payment` | `userManagement` |
| Interface | Behavior + -er | `Reader`, `UserFinder` | `IUser` |
| Struct | Clear noun | `User`, `PaymentRequest` | `UserStruct` |
| Method | Verb phrase | `GetUser`, `ProcessPayment` | `RetrieveUserData` |
| Error | Err prefix | `ErrUserNotFound` | `ErrorUserNotFound` |
| Constant | MixedCase | `DefaultTimeout` | `TIMEOUT_VALUE` |

---

