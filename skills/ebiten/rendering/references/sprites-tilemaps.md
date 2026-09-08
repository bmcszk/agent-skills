# Sprites & Tilemaps

## Sprite Animation

### Frame-Based Animation

```go
type Animation struct {
    frames    []*ebiten.Image
    frameTime int
    current   int
    timer     int
    loop      bool
}

func NewAnimation(frames []*ebiten.Image, frameTime int, loop bool) *Animation {
    return &Animation{
        frames:    frames,
        frameTime: frameTime,
        loop:      loop,
    }
}

func (a *Animation) Update() {
    a.timer++
    if a.timer >= a.frameTime {
        a.timer = 0
        a.current++
        if a.current >= len(a.frames) {
            if a.loop {
                a.current = 0
            } else {
                a.current = len(a.frames) - 1
            }
        }
    }
}

func (a *Animation) Image() *ebiten.Image {
    return a.frames[a.current]
}

func (a *Animation) IsFinished() bool {
    return !a.loop && a.current == len(a.frames)-1 && a.timer >= a.frameTime-1
}
```

### Animation State Machine

```go
type AnimState int

const (
    AnimIdle AnimState = iota
    AnimRun
    AnimJump
    AnimAttack
)

type AnimController struct {
    states   map[AnimState]*Animation
    current  AnimState
}

func (c *AnimController) Play(state AnimState) {
    if c.current != state {
        c.current = state
        c.states[state].current = 0
        c.states[state].timer = 0
    }
}

func (c *AnimController) Update() {
    c.states[c.current].Update()
}

func (c *AnimController) Image() *ebiten.Image {
    return c.states[c.current].Image()
}
```

### ganim8 Library

```go
import "github.com/yohamta/ganim8"

// Define grid from sprite sheet
grid := ganim8.NewGrid(32, 32, sheet.Bounds().Dx(), sheet.Bounds().Dy())

// Create animation
anim := ganim8.New(sheet, grid.Frames("1-4", 1), 0.1)

// Play
anim.Update()
anim.Draw(screen, opts)
```

---

## Tilemap Rendering

### Basic Grid Renderer

```go
type Tilemap struct {
    Tiles     [][]int
    TileSize  int
    Tileset   *ebiten.Image
}

func (t *Tilemap) Draw(screen *ebiten.Image, cameraX, cameraY float64) {
    opts := &ebiten.DrawImageOptions{}
    tileSize := t.TileSize

    startCol := int(cameraX) / tileSize
    startRow := int(cameraY) / tileSize
    endCol := startCol + screen.Bounds().Dx()/tileSize + 2
    endRow := startRow + screen.Bounds().Dy()/tileSize + 2

    for row := startRow; row < endRow && row < len(t.Tiles); row++ {
        for col := startCol; col < endCol && col < len(t.Tiles[row]); col++ {
            tileID := t.Tiles[row][col]
            if tileID == 0 {
                continue
            }

            srcX := (tileID % tilesPerRow) * tileSize
            srcY := (tileID / tilesPerRow) * tileSize
            tile := t.Tileset.SubImage(image.Rect(srcX, srcY, srcX+tileSize, srcY+tileSize)).(*ebiten.Image)

            opts.GeoM.Reset()
            opts.GeoM.Translate(float64(col*tileSize)-cameraX, float64(row*tileSize)-cameraY)
            screen.DrawImage(tile, opts)
        }
    }
}
```

### LDtk (ldtkgo)

```go
import "github.com/SolarLune/ldtkgo"

project, err := ldtkgo.Open("level.ldtk")

level := project.Levels[0]
for _, layer := range level.layers {
    for _, tile := range layer.Tiles {
        // tile has position, source rect, etc.
    }
}
```

### Tiled (go-tiled)

```go
import tiled "github.com/lafriks/go-tiled"

gameMap, err := tiled.LoadFromFile("map.tmx")

for _, layer := range gameMap.Layers {
    for y := 0; y < layer.Height; y++ {
        for x := 0; x < layer.Width; x++ {
            tileID := layer.Tiles[y*layer.Width+x].ID
            // draw tile
        }
    }
}
```

---
