# Performance & Footguns
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

