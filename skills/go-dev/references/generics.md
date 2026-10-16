# Generics (Go 1.18+)

## Basic Type Parameters

```go
func Max[T constraints.Ordered](a, b T) T {
    if a > b {
        return a
    }
    return b
}

func Map[T, U any](slice []T, fn func(T) U) []U {
    result := make([]U, len(slice))
    for i, v := range slice {
        result[i] = fn(v)
    }
    return result
}
```

## Type Constraints

```go
type Number interface {
    constraints.Integer | constraints.Float
}

func Sum[T Number](numbers []T) T {
    var total T
    for _, n := range numbers {
        total += n
    }
    return total
}
```

## Generic Data Structures

```go
type Stack[T any] struct {
    items []T
}

func NewStack[T any]() *Stack[T] {
    return &Stack[T]{items: make([]T, 0)}
}

func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item, true
}
```

## Generic Utilities

```go
func Filter[T any](slice []T, predicate func(T) bool) []T {
    result := make([]T, 0, len(slice))
    for _, v := range slice {
        if predicate(v) {
            result = append(result, v)
        }
    }
    return result
}

func Reduce[T, U any](slice []T, initial U, fn func(U, T) U) U {
    acc := initial
    for _, v := range slice {
        acc = fn(acc, v)
    }
    return acc
}

func Keys[K comparable, V any](m map[K,V) []K {
    keys := make([]K, 0, len(m))
    for k := range m {
        keys = append(keys, k)
    }
    return keys
}
```

## Generic methods (Go 1.27+)

Go 1.27 allows type parameters on concrete methods: `func (l *List[E]) Map[R any](f func(E) R) List[R]`.
Interface methods still may NOT declare type parameters, and a generic method
cannot satisfy an interface method. The feature organizes code, it does not
extend interface polymorphism.

Fluent-builder chains are the case where the lack of a self-type still bites:
- A base-receiver method cannot return the OUTER domain type (no `Self`);
  a generic method on the base `func (p *base) step[S any]() S` can only
  return the zero value of `S`. The receiver cannot produce a sound `S`
  instance. Zero-value returns of pointer types are nil panics downstream.
- Per-domain wrapper structs with domain-typed methods break mixed-domain
  chains (a base-typed return degrades the chain after the first promoted
  call). Keep every builder on the shared struct returning the shared
  pointer; chains stay uniform and typed.

## Generics Decision Framework

| Use Generics When | Don't Use Generics When |
|-------------------|------------------------|
| Type-safe containers (Stack, Queue) | Simple business logic |
| Algorithm implementations | Database models |
| Utility functions (Map, Filter) | HTTP handlers |
| Reducing code duplication | When interfaces suffice |
| Type-safe fluent DSL anchors via one shared struct | Preserving outer-typed returns from base-receiver fluent methods (no sound pattern exists) |

---

