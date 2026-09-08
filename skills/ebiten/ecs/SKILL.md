---
name: ecs
description: 'Entity Component System patterns for Ebitengine: Donburi, Ark, Mizu. Architecture, queries, systems.'
metadata:
  risk: none
  source: community
  date_added: '2026-05-12'
---
# Entity Component System (ECS)

> ECS architecture patterns and libraries for Ebitengine games.

---

## When to Use ECS

| Scenario | Use ECS? | Recommended |
|----------|----------|-------------|
| Hundreds+ entities (bullets, particles) | Yes | Donburi or Ark |
| Deep inheritance hierarchies | Yes | Any ECS |
| Systems operate on entity subsets | Yes | Donburi |
| Prototype/quick game jam | No | Plain structs |
| Simple game with < 50 entities | No | Composition via structs |
| Turn-based with complex state | Maybe | Evaluate per case |
| Real-time strategy with many unit types | Yes | Donburi or Ark |

---

## Library Comparison

| Feature | Donburi | Ark | Mizu | Gohan |
|---------|---------|-----|------|-------|
| **Approach** | Sparse set ECS | Archetype ECS | ECS framework | ECS framework |
| **Performance** | Good | Excellent | Good | Good |
| **API Style** | Builder pattern | Archetype queries | Declarative | Declarative |
| **World Model** | Single world | Multiple worlds | Single world | Single world |
| **Serialization** | Via plugins | Built-in | Manual | Partial |
| **Ebiten Integration** | First-class | Manual | First-class | Manual |
| **Tag Support** | Yes | Yes | Yes | Yes |
| **Networking** | necs plugin | Manual | Manual | Manual |
| **GitHub** | [yohamta/donburi](https://github.com/yohamta/donburi) | [mlange-42/ark](https://github.com/mlange-42/ark) | [sedyh/mizu](https://github.com/sedyh/mizu) | [mttchpmn/gohan](https://github.com/mttchpmn/gohan) |

---

## Donburi Deep Dive

Donburi is the most popular ECS for Ebitengine, created by the same author as ganim8.

### Components

```go
package component

import (
    "github.com/yohamta/donburi"
    "github.com/yohamta/donburi/ecs"
)

type PositionData struct {
    X, Y float64
}

var Position = donburi.NewComponentType[PositionData]()

type VelocityData struct {
    X, Y float64
}

var Velocity = donburi.NewComponentType[VelocityData]()

type SpriteData struct {
    Image   *ebiten.Image
    Width   int
    Height  int
}

var Sprite = donburi.NewComponentType[SpriteData]()

type PlayerTag struct{}

var Player = donburi.NewTag().SetName("Player")

type HealthData struct {
    Current int
    Max     int
}

var Health = donburi.NewComponentType[HealthData]()

type EnemyTag struct{}

var Enemy = donburi.NewTag().SetName("Enemy")
```

### Creating Entities

```go
func CreatePlayer(ecs *ecs.ECS, x, y float64, img *ebiten.Image) donburi.Entity {
    entity := ecs.World.Create(
        component.Position,
        component.Velocity,
        component.Sprite,
        component.Health,
        component.Player,
    )
    entry := ecs.World.Entry(entity)
    donburi.SetValue(entry, component.Position, &component.PositionData{X: x, Y: y})
    donburi.SetValue(entry, component.Velocity, &component.VelocityData{})
    donburi.SetValue(entry, component.Sprite, &component.SpriteData{Image: img})
    donburi.SetValue(entry, component.Health, &component.HealthData{Current: 100, Max: 100})
    return entity
}

func CreateBullet(ecs *ecs.ECS, x, y, vx, vy float64, img *ebiten.Image) donburi.Entity {
    entity := ecs.World.Create(
        component.Position,
        component.Velocity,
        component.Sprite,
    )
    entry := ecs.World.Entry(entity)
    donburi.SetValue(entry, component.Position, &component.PositionData{X: x, Y: y})
    donburi.SetValue(entry, component.Velocity, &component.VelocityData{X: vx, Y: vy})
    donburi.SetValue(entry, component.Sprite, &component.SpriteData{Image: img})
    return entity
}
```

### Queries

```go
// Query all entities with Position and Velocity
query := donburi.NewQuery(
    filter.Contains(component.Position),
    filter.Contains(component.Velocity),
)

// Query with optional component
query := donburi.NewQuery(
    filter.Contains(component.Position),
    filter.Optional(component.Sprite),
)

// Query by tag
playerQuery := donburi.NewQuery(
    filter.Contains(component.Player),
)

// Iterate
query.Each(ecs.World, func(entry *donburi.Entry) {
    pos := component.Position.Get(entry)
    vel := component.Velocity.Get(entry)
    pos.X += vel.X
    pos.Y += vel.Y
})
```

### Systems

```go
type MovementSystem struct{}

func (s *MovementSystem) Update(ecs *ecs.ECS) {
    query := donburi.NewQuery(
        filter.Contains(component.Position),
        filter.Contains(component.Velocity),
    )
    query.Each(ecs.World, func(entry *donburi.Entry) {
        pos := component.Position.Get(entry)
        vel := component.Velocity.Get(entry)
        pos.X += vel.X
        pos.Y += vel.Y
    })
}

type RenderSystem struct{}

func (s *RenderSystem) Draw(ecs *ecs.ECS, screen *ebiten.Image) {
    opts := &ebiten.DrawImageOptions{}
    query := donburi.NewQuery(
        filter.Contains(component.Position),
        filter.Contains(component.Sprite),
    )
    query.Each(ecs.World, func(entry *donburi.Entry) {
        pos := component.Position.Get(entry)
        spr := component.Sprite.Get(entry)
        opts.GeoM.Reset()
        opts.GeoM.Translate(pos.X, pos.Y)
        screen.DrawImage(spr.Image, opts)
    })
}

type CollisionSystem struct{}

func (s *CollisionSystem) Update(ecs *ecs.ECS) {
    playerQuery := donburi.NewQuery(filter.Contains(component.Player))
    enemyQuery := donburi.NewQuery(filter.Contains(component.Enemy))

    playerQuery.Each(ecs.World, func(pEntry *donburi.Entry) {
        pPos := component.Position.Get(pEntry)
        enemyQuery.Each(ecs.World, func(eEntry *donburi.Entry) {
            ePos := component.Position.Get(eEntry)
            if math.Abs(pPos.X-ePos.X) < 16 && math.Abs(pPos.Y-ePos.Y) < 16 {
                health := component.Health.Get(pEntry)
                health.Current -= 10
            }
        })
    })
}
```

### Tags

Tags are zero-size components used to categorize entities:

```go
var Player = donburi.NewTag().SetName("Player")
var Enemy = donburi.NewTag().SetName("Enemy")
var Bullet = donburi.NewTag().SetName("Bullet")
var Collectible = donburi.NewTag().SetName("Collectible")

// Adding a tag
ecs.World.Create(component.Position, component.Player)

// Querying by tag
query := donburi.NewQuery(filter.Contains(component.Enemy))
```

### Entity Removal

```go
// Remove a single entity
entry := ecs.World.Entry(entity)
entry.Remove()

// Remove entities matching query (e.g., off-screen bullets)
query := donburi.NewQuery(
    filter.Contains(component.Bullet),
    filter.Contains(component.Position),
)
var toRemove []donburi.EntityID
query.Each(ecs.World, func(entry *donburi.Entry) {
    pos := component.Position.Get(entry)
    if pos.X < -50 || pos.X > 1000 || pos.Y < -50 || pos.Y > 1000 {
        toRemove = append(toRemove, entry.EntityID())
    }
})
for _, id := range toRemove {
    ecs.World.Remove(id)
}
```

---

## Game Integration Pattern

```go
package main

import (
    "github.com/hajimehoshi/ebiten/v2"
    "github.com/yohamta/donburi"
    "github.com/yohamta/donburi/ecs"
    "github.com/yohamta/donburi/filter"
)

type System interface {
    Update(e *ecs.ECS)
    Draw(e *ecs.ECS, screen *ebiten.Image)
}

type Game struct {
    ecs      *ecs.ECS
    systems  []System
}

func NewGame() *Game {
    g := &Game{
        ecs: ecs.NewECS(ecs.NewWorld()),
    }
    g.systems = []System{
        &InputSystem{},
        &MovementSystem{},
        &CollisionSystem{},
        &CleanupSystem{},
        &RenderSystem{},
    }

    // Create initial entities
    CreatePlayer(g.ecs, 100, 100, playerSprite)

    return g
}

func (g *Game) Update() error {
    for _, sys := range g.systems {
        sys.Update(g.ecs)
    }
    return nil
}

func (g *Game) Draw(screen *ebiten.Image) {
    for _, sys := range g.systems {
        sys.Draw(g.ecs, screen)
    }
}

func (g *Game) Layout(w, h int) (int, int) {
    return 320, 240
}
```

---

## Networking with necs

```go
import "github.com/leap-fish/necs"

// Setup networking layer on top of Donburi ECS
// necs provides:
// - Entity synchronization across network
// - Component replication
// - RPC system
// - Client/Server architecture
```

---

## Ark (Alternative)

```go
import "github.com/mlange-42/ark/ecs"

// Archetype-based ECS with excellent cache performance
w := ecs.NewWorld()

posMapper := ecs.NewMap1[Position](&w)
velMapper := ecs.NewMap2[Position, Velocity](&w)

// Create entity
entity := posMapper.NewEntity(&Position{X: 10, Y: 20})

// Query
query := ecs.NewFilter1[Position](&w)
for q.Next() {
    pos := q.Get()
    pos.X += 1
}
```

Ark is faster for large entity counts due to archetype storage, but has a steeper API.

---

## When NOT to Use ECS

| Scenario | Better Approach |
|----------|----------------|
| Simple game with few entity types | Plain Go structs with composition |
| Game jam / prototype | Direct struct-based design |
| Turn-based RPG with complex state | Object-oriented with interfaces |
| UI-heavy game | ebitenui or furex |
| Puzzle game with grid state | 2D array with game logic |

### Simple Alternative (No ECS)

```go
type Game struct {
    player   *Player
    enemies  []*Enemy
    bullets  []*Bullet
    particles []*Particle
}

func (g *Game) Update() error {
    g.player.Update()
    for _, e := range g.enemies {
        e.Update()
    }
    for _, b := range g.bullets {
        b.Update()
    }
    return nil
}
```

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Store `*ebiten.Image` in every entity | Store sprite ID, use a lookup table |
| Create/destroy entities every frame for particles | Use an object pool |
| Put game logic in component getters/setters | Keep components as pure data |
| Query all entities when you need one | Use tag + targeted query |
| Mix rendering logic into ECS systems | Keep render systems separate |
| Use ECS for UI elements | Use a UI library instead |
| Create world per level (Donburi) | Use a single world, manage entity lifecycles |
| Store references to entries across frames | Re-query or use Entity IDs |
| Skip removing dead entities | Clean up each frame to prevent memory leaks |

## When to Use
This skill is applicable when designing or implementing an Entity Component System architecture in an Ebitengine game.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
