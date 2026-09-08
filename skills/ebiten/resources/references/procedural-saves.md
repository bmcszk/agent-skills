# Procedural Generation & Save Data

## Procedural Generation

### dngn Library

```go
import "github.com/SolarLune/dngn"

// Create a dungeon map
dungeon := dngn.NewDungeonMap(40, 30, 1, 2, 1, dngn.RoomPlacementRandom)
dungeon.Generate()

// Access the grid
grid := dungeon.Grid
for y := 0; y < grid.Height(); y++ {
    for x := 0; x < grid.Width(); x++ {
        cell := grid.Get(x, y)
        // 0 = wall, 1 = floor, 2+ = special
    }
}
```

### Custom Generation

```go
type Level struct {
    Width  int
    Height int
    Tiles  [][]int
}

func GenerateLevel(width, height int) *Level {
    l := &Level{
        Width:  width,
        Height: height,
        Tiles:  make([][]int, height),
    }
    for y := range l.Tiles {
        l.Tiles[y] = make([]int, width)
    }

    // Fill borders
    for x := 0; x < width; x++ {
        l.Tiles[0][x] = 1
        l.Tiles[height-1][x] = 1
    }
    for y := 0; y < height; y++ {
        l.Tiles[y][0] = 1
        l.Tiles[y][width-1] = 1
    }

    // Place rooms
    for i := 0; i < 5; i++ {
        rw := 4 + rand.Intn(6)
        rh := 4 + rand.Intn(4)
        rx := 2 + rand.Intn(width-rw-4)
        ry := 2 + rand.Intn(height-rh-4)
        for y := ry; y < ry+rh; y++ {
            for x := rx; x < rx+rw; x++ {
                l.Tiles[y][x] = 0
            }
        }
    }

    return l
}
```

---

## Save Data (gdata)

```go
import "github.com/quasilyte/gdata"

type SaveData struct {
    Level    int     `json:"level"`
    Score    int     `json:"score"`
    PlayerX  float64 `json:"player_x"`
    PlayerY  float64 `json:"player_y"`
}

func saveGame(data *SaveData) error {
    jsonBytes, err := json.Marshal(data)
    if err != nil {
        return err
    }
    return gdata.Save(jsonBytes, "savegame.dat")
}

func loadGame() (*SaveData, error) {
    data, err := gdata.Load("savegame.dat")
    if err != nil {
        return nil, err
    }
    var save SaveData
    if err := json.Unmarshal(data, &save); err != nil {
        return nil, err
    }
    return &save, nil
}
```

`gdata` automatically handles cross-platform save paths:
- **Linux:** `~/.local/share/<game>/`
- **macOS:** `~/Library/Application Support/<game>/`
- **Windows:** `%AppData%/<game>/`

---
