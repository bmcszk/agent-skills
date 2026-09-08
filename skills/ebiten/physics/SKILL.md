---
name: physics
description: 'Ebitengine collision detection, physics, pathfinding: resolv, Chipmunk2D, Box2D, spatial hashing.'
metadata:
  risk: none
  source: community
  date_added: '2026-05-12'
---
# Physics & Collision

> Collision detection, physics simulation, and pathfinding for Ebitengine.

---

## Library Comparison

| Library | Type | Best For | Complexity |
|---------|------|----------|------------|
| None (AABB) | Manual | Simple platformers, grid games | Low |
| [resolv](https://github.com/SolarLune/resolv) | Collision resolution | Tile-based, platformers | Low |
| [coll](https://github.com/setanarut/coll) | Collision detection | Simple shape overlap checks | Low |
| [cp](https://github.com/jakecoffman/cp) | Full physics | Physics-driven games, ragdolls | Medium |
| [box2d-go](https://github.com/oliverbestmann/box2d-go) | Full physics | Complex simulations | High |

---

## Collision Strategy by Game Type

| Game Type | Recommended Approach |
|-----------|---------------------|
| Tile-based platformer | AABB + resolv |
| Top-down RPG | AABB or resolv |
| Shooter with bullets | Spatial hash + AABB |
| Physics puzzle | Chipmunk2D (cp) |
| Vehicle/racing | Box2D-go |
| Grid-based puzzle | No library needed |
| Fighting game | coll + custom hitboxes |
| Strategy game | Quadtree + AABB |

---

## Simple AABB (No Library)

### Axis-Aligned Bounding Box

```go
type Rect struct {
    X, Y, W, H float64
}

func (r Rect) Intersects(other Rect) bool {
    return r.X < other.X+other.W &&
        r.X+r.W > other.X &&
        r.Y < other.Y+other.H &&
        r.Y+r.H > other.Y
}

func (r Rect) Contains(x, y float64) bool {
    return x >= r.X && x <= r.X+r.W && y >= r.Y && y <= r.Y+r.H
}
```

### Resolving Collisions

```go
func resolveCollision(mover Rect, obstacle Rect) (float64, float64) {
    overlapX := math.Min(mover.X+mover.W-obstacle.X, obstacle.X+obstacle.W-mover.X)
    overlapY := math.Min(mover.Y+mover.H-obstacle.Y, obstacle.Y+obstacle.H-mover.Y)

    dx, dy := 0.0, 0.0
    if overlapX < overlapY {
        if mover.X+mover.W/2 < obstacle.X+obstacle.W/2 {
            dx = -overlapX
        } else {
            dx = overlapX
        }
    } else {
        if mover.Y+mover.H/2 < obstacle.Y+obstacle.H/2 {
            dy = -overlapY
        } else {
            dy = overlapY
        }
    }
    return dx, dy
}
```

---

## Platformer Collision Pattern

```go
type Player struct {
    X, Y     float64
    VX, VY   float64
    Width    float64
    Height   float64
    OnGround bool
}

const gravity = 0.5

func (p *Player) Update(tiles [][]int, tileSize int) {
    p.VY += gravity
    p.VX *= 0.8

    newX := p.X + p.VX
    if !p.collidesAt(newX, p.Y, tiles, tileSize) {
        p.X = newX
    } else {
        p.VX = 0
    }

    newY := p.Y + p.VY
    if !p.collidesAt(p.X, newY, tiles, tileSize) {
        p.Y = newY
        p.OnGround = false
    } else {
        if p.VY > 0 {
            p.OnGround = true
            p.Y = float64(int(p.Y/float64(tileSize))) * float64(tileSize)
        }
        p.VY = 0
    }
}

func (p *Player) collidesAt(x, y float64, tiles [][]int, tileSize int) bool {
    checkPoints := [][2]float64{
        {x, y},
        {x + p.Width, y},
        {x, y + p.Height},
        {x + p.Width, y + p.Height},
        {x + p.Width / 2, y},
        {x + p.Width / 2, y + p.Height},
    }
    for _, pt := range checkPoints {
        col := int(pt[0] / float64(tileSize))
        row := int(pt[1] / float64(tileSize))
        if row < 0 || row >= len(tiles) || col < 0 || col >= len(tiles[row]) {
            continue
        }
        if tiles[row][col] != 0 {
            return true
        }
    }
    return false
}
```

---

## resolv Library

resolv is a 2D collision resolution library designed for tile and platformer games.

### Basic Setup

```go
import "github.com/SolarLune/resolv"

type Game struct {
    space  *resolv.Space
    player *resolv.Object
}

func NewGame() *Game {
    g := &Game{}

    g.space = resolv.NewSpace(640, 480, 16, 16)

    // Add solid tiles
    for row, tiles := range levelData {
        for col, tile := range tiles {
            if tile != 0 {
                obj := resolv.NewObject(
                    float64(col*16), float64(row*16), 16, 16,
                )
                obj.AddTags("solid")
                g.space.Add(obj)
            }
        }
    }

    g.player = resolv.NewObject(32, 32, 12, 16)
    g.space.Add(g.player)

    return g
}
```

### Movement with Collision

```go
func (g *Game) Update() error {
    dx, dy := 0.0, 0.0

    if ebiten.IsKeyPressed(ebiten.KeyArrowRight) {
        dx = 2
    }
    if ebiten.IsKeyPressed(ebiten.KeyArrowLeft) {
        dx = -2
    }

    dy += 3 // gravity

    // Resolve horizontal
    if collision := g.space.Check(g.player, dx, 0, "solid"); collision != nil {
        g.player.X += collision.ContactWithCell(g.player.X+dx, g.player.Y).X()
        dx = 0
    } else {
        g.player.X += dx
    }

    // Resolve vertical
    if collision := g.space.Check(g.player, 0, dy, "solid"); collision != nil {
        g.player.Y += collision.ContactWithCell(g.player.X, g.player.Y+dy).Y()
        if dy > 0 {
            // landed on ground
        }
        dy = 0
    } else {
        g.player.Y += dy
    }

    g.player.Update()
    return nil
}
```

### Tags and Filtering

```go
// Objects can have multiple tags
obj.AddTags("solid", "hazard", "platform")

// Check against specific tags
collision := space.Check(player, dx, dy, "solid", "hazard")

// Check if touching specific tag
if space.IsOutOfBounds(player, 0, 0) {
    // handle boundary
}
```

---

## Chipmunk2D (cp)

Full 2D physics: gravity, joints, friction, bouncing.

### Basic Setup

```go
import "github.com/jakecoffman/cp"

type PhysicsGame struct {
    space *cp.Space
}

func NewPhysicsGame() *PhysicsGame {
    g := &PhysicsGame{
        space: cp.NewSpace(),
    }
    g.space.Gravity = cp.Vector{X: 0, Y: 900}

    // Static walls/floor
    floor := cp.NewSegment(g.space.StaticBody, cp.Vector{X: 0, Y: 400}, cp.Vector{X: 640, Y: 400}, 0)
    floor.SetFriction(0.8)
    g.space.AddShape(floor)

    // Dynamic body
    body := cp.NewBody(1, cp.INFINITY)
    body.SetPosition(cp.Vector{X: 320, Y: 200})
    shape := cp.NewCircle(body, 10, cp.Vector{})
    shape.SetFriction(0.5)
    shape.SetElasticity(0.8)
    g.space.AddBody(body)
    g.space.AddShape(shape)

    return g
}

func (g *PhysicsGame) Update() error {
    g.space.Step(1.0 / 60.0)
    return nil
}
```

### Joints

```go
// Pin joint (keeps distance between two bodies)
pin := cp.NewPinJoint(bodyA, bodyB, anchorA, anchorB)
g.space.AddConstraint(pin)

// Pivot joint (rotates around point)
pivot := cp.NewPivotJoint(bodyA, bodyB, pivotPoint)
g.space.AddConstraint(pivot)

// Slide joint (distance constraint with min/max)
slide := cp.NewSlideJoint(bodyA, bodyB, anchorA, anchorB, minLength, maxLength)
g.space.AddConstraint(slide)

// Damped spring
spring := cp.NewDampedSpring(bodyA, bodyB, anchorA, anchorB, restLength, stiffness, damping)
g.space.AddConstraint(spring)
```

### Collision Callbacks

```go
g.space.AddCollisionHandler(collisionTypePlayer, collisionTypeEnemy).
    BeginFunc(func(arbiter *cp.Arbiter, space *cp.Space, userData interface{}) bool {
        // Collision started
        return true // process collision
    }).
    SeparateFunc(func(arbiter *cp.Arbiter, space *cp.Space, userData interface{}) {
        // Bodies separated
    })
```

---

## Spatial Hashing

For efficient collision detection with many entities:

```go
type SpatialHash struct {
    cellSize float64
    cells    map[[2]int][]*Entity
}

func NewSpatialHash(cellSize float64) *SpatialHash {
    return &SpatialHash{
        cellSize: cellSize,
        cells:    make(map[[2]int][]*Entity),
    }
}

func (h *SpatialHash) Clear() {
    for k := range h.cells {
        delete(h.cells, k)
    }
}

func (h *SpatialHash) cellKey(x, y float64) [2]int {
    return [2]int{int(math.Floor(x / h.cellSize)), int(math.Floor(y / h.cellSize))}
}

func (h *SpatialHash) Insert(e *Entity, x, y, w, hSize float64) {
    minKey := h.cellKey(x, y)
    maxKey := h.cellKey(x+w, y+hSize)
    for cx := minKey[0]; cx <= maxKey[0]; cx++ {
        for cy := minKey[1]; cy <= maxKey[1]; cy++ {
            key := [2]int{cx, cy}
            h.cells[key] = append(h.cells[key], e)
        }
    }
}

func (h *SpatialHash) Query(x, y, w, h float64) []*Entity {
    seen := make(map[*Entity]bool)
    var results []*Entity
    minKey := h.cellKey(x, y)
    maxKey := h.cellKey(x+w, y+h)
    for cx := minKey[0]; cx <= maxKey[0]; cx++ {
        for cy := minKey[1]; cy <= maxKey[1]; cy++ {
            for _, e := range h.cells[[2]int{cx, cy}] {
                if !seen[e] {
                    seen[e] = true
                    results = append(results, e)
                }
            }
        }
    }
    return results
}
```

---

## Pathfinding

### paths Library

```go
import "github.com/SolarLune/paths"

// Create a grid-based pathfinding map
pathMap := paths.NewGridMap(width, height, cellW, cellH)

// Set walkable/unwalkable cells
pathMap.Set(5, 3, paths.CellTypeWalkable)
pathMap.Set(5, 4, paths.CellTypeSolid)

// Find path
path, found := pathMap.GetPath(startX, startY, endX, endY, true)
if found {
    for _, cell := range path {
        // cell.X, cell.Y
    }
}
```

### go-astar

```go
// Simple A* for tile-based games
func findPath(tiles [][]int, start, end [2]int) [][2]int {
    openSet := []*pathNode{newPathNode(start, 0, heuristic(start, end), nil)}
    closedSet := make(map[[2]int]bool)

    for len(openSet) > 0 {
        current := popLowest(openSet)
        if current.pos == end {
            return reconstructPath(current)
        }
        closedSet[current.pos] = true

        for _, neighbor := range getNeighbors(current.pos, tiles) {
            if closedSet[neighbor] {
                continue
            }
            g := current.g + 1
            h := heuristic(neighbor, end)
            openSet = append(openSet, newPathNode(neighbor, g, g+h, current))
        }
    }
    return nil
}
```

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Check every entity against every other entity | Use spatial hashing for O(n) broad phase |
| Use full physics for simple tile collision | Use AABB or resolv for tile-based games |
| Ignore floating-point drift in collision | Round positions to grid for tile collision |
| Resolve X and Y collision simultaneously | Resolve axes separately (X first, then Y) |
| Use pixel-perfect collision for fast-moving objects | Use sweep tests or continuous collision detection |
| Apply physics in `Draw()` | All physics in `Update()` |
| Skip collision for newly spawned entities | Check collision immediately after spawn |
| Use `float32` for physics calculations | Use `float64` for precision |
| Create new physics bodies every frame | Pool and reuse bodies |
| Mix rendering coordinates with physics coordinates | Keep separate coordinate systems |

## When to Use
This skill is applicable when implementing collision detection, physics simulation, or pathfinding in an Ebitengine game.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
