# Sprite Sheets & Tile Maps

## Sprite Sheets

### Manual Sprite Sheet

```go
type SpriteSheet struct {
    image     *ebiten.Image
    frameW    int
    frameH    int
    columns   int
}

func NewSpriteSheet(img *ebiten.Image, frameW, frameH int) *SpriteSheet {
    bounds := img.Bounds()
    return &SpriteSheet{
        image:   img,
        frameW:  frameW,
        frameH:  frameH,
        columns: bounds.Dx() / frameW,
    }
}

func (s *SpriteSheet) Frame(index int) *ebiten.Image {
    col := index % s.columns
    row := index / s.columns
    x := col * s.frameW
    y := row * s.frameH
    return s.image.SubImage(image.Rect(x, y, x+s.frameW, y+s.frameH)).(*ebiten.Image)
}
```

### Aseprite Files

#### aseprite Library (Parser)

```go
import "github.com/setanarut/aseprite"

file, err := aseprite.Open("character.aseprite")

// Access layers
for _, layer := range file.Layers {
    // layer.Name, layer.Visible, etc.
}

// Access tags (animation names)
for _, tag := range file.Tags {
    // tag.Name, tag.From, tag.To
}

// Access frames
for _, frame := range file.Frames {
    // frame.Image() returns image.Image
}
```

#### aseplayer (Animation Player)

```go
import "github.com/setanarut/aseplayer"

player := aseplayer.New(file)
player.Play("run")

// In Update
player.Update()

// In Draw
player.Draw(screen, opts)

// Control
player.Play("jump")
player.Pause()
player.Resume()
```

#### goaseprite

```go
import "github.com/askeladdk/goaseprite"

sprite := goaseprite.New(data)
sprite.Play("walk")
sprite.Update()

// Get current frame rectangle
frame := sprite.CurrentFrame

// Get current frame image from sprite sheet
region := sheet.SubImage(image.Rect(
    frame.X, frame.Y,
    frame.X+frame.W, frame.Y+frame.H,
)).(*ebiten.Image)
```

---

## Tile Maps

### LDtk (ldtkgo)

```go
import "github.com/SolarLune/ldtkgo"

// Load from file
project, err := ldtkgo.Open("levels.ldtk")

// Or from embedded bytes
project, err := ldtkgo.Read(data)

// Access levels
for _, level := range project.Levels {
    fmt.Printf("Level: %s (%dx%d)\n", level.Identifier, level.Width, level.Height)

    // Access layers
    for _, layer := range level.Layers {
        // Tile layers
        for _, tile := range layer.Tiles {
            // tile.X, tile.Y - position in level
            // tile.SrcX, tile.SrcY - source position in tileset
        }

        // Entity layers
        for _, entity := range layer.Entities {
            // entity.X, entity.Y
            // entity.Width, entity.Height
            // entity.FieldValues for custom fields
        }
    }
}
```

### Tiled (go-tiled)

```go
import tiled "github.com/lafriks/go-tiled"

// Load from file
gameMap, err := tiled.LoadFromFile("map.tmx")

// Or from embedded data
gameMap, err := tiled.LoadFromData(data, "map.tmx")

// Access layers
for _, layer := range gameMap.Layers {
    for y := 0; y < layer.Height; y++ {
        for x := 0; x < layer.Width; x++ {
            tile := layer.Tiles[y*layer.Width+x]
            if tile.IsNil() {
                continue
            }
            // tile.ID - global tile ID
            // tile.Tileset - reference to tileset
        }
    }
}

// Object groups (for triggers, spawn points)
for _, group := range gameMap.ObjectGroups {
    for _, obj := range group.Objects {
        // obj.X, obj.Y, obj.Width, obj.Height
        // obj.Name, obj.Type
        // obj.PolyLines, obj.Polygons for shapes
    }
}

// Tilesets
for _, ts := range gameMap.Tilesets {
    // ts.Name, ts.Image, ts.TileWidth, ts.TileHeight
}
```

---
