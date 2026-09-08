# Concurrency

## Use errgroup (NOT sync.WaitGroup)

```go
import "golang.org/x/sync/errgroup"

func (s *UserService) ProcessUserBatch(ctx context.Context, userIDs []string) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(10) // ALWAYS set limits
    
    for _, userID := range userIDs {
        userID := userID // Capture loop variable
        g.Go(func() error {
            return s.processUser(ctx, userID)
        })
    }
    
    return g.Wait() // Returns first error, cancels all operations
}
```

## Why errgroup over sync.WaitGroup

| Feature | sync.WaitGroup | errgroup |
|---------|---------------|----------|
| Error Handling | Manual collection | Automatic propagation |
| Cancellation | Manual | Built-in context cancellation |
| Resource Limits | No | `SetLimit()` prevents OOM |
| First Error | Must collect all | First error cancels all |

## Worker Pool Pattern

```go
type WorkerPool struct {
    workers int
    tasks   chan func()
    wg      sync.WaitGroup
}

func NewWorkerPool(workers int) *WorkerPool {
    wp := &WorkerPool{
        workers: workers,
        tasks:   make(chan func(), workers*2),
    }
    wp.start()
    return wp
}

func (wp *WorkerPool) start() {
    for i := 0; i < wp.workers; i++ {
        wp.wg.Add(1)
        go func() {
            defer wp.wg.Done()
            for task := range wp.tasks {
                task()
            }
        }()
    }
}

func (wp *WorkerPool) Submit(task func()) {
    wp.tasks <- task
}

func (wp *WorkerPool) Shutdown() {
    close(wp.tasks)
    wp.wg.Wait()
}
```

## Channel Patterns

```go
// Generator pattern
func generateNumbers(ctx context.Context, max int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for i := 0; i < max; i++ {
            select {
            case out <- i:
            case <-ctx.Done():
                return
            }
        }
    }()
    return out
}

// Fan-out, fan-in pattern
func fanIn(ctx context.Context, channels ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup
    
    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for val := range c {
                select {
                case out <- val:
                case <-ctx.Done():
                    return
                }
            }
        }(ch)
    }
    
    go func() {
        wg.Wait()
        close(out)
    }()
    
    return out
}
```

---

