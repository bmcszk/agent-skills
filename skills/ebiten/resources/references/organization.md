# Asset Organization & Loading Screens

## Asset Organization

```
mygame/
├── main.go
├── go.mod
├── assets/
│   ├── images/
│   │   ├── player.png
│   │   ├── enemy.png
│   │   ├── tiles/
│   │   │   ├── grass.png
│   │   │   └── stone.png
│   │   └── ui/
│   │       ├── button.png
│   │       └── panel.png
│   ├── audio/
│   │   ├── sfx/
│   │   │   ├── jump.wav
│   │   │   └── shoot.wav
│   │   └── music/
│   │       └── theme.ogg
│   ├── levels/
│   │   ├── level1.ldtk
│   │   └── level1.tmx
│   ├── fonts/
│   │   └── game.ttf
│   └── data/
│       └── items.json
├── shaders/
│   ├── blur.kage
│   └── dissolve.kage
```

---

## Loading Screen Pattern

```go
type LoadingState int

const (
    LoadingAssets LoadingState = iota
    LoadingDone
)

type Game struct {
    loadState LoadingState
    loader    *AssetLoader
    progress  float64
}

type AssetLoader struct {
    total   int
    loaded  int
    loadFn  []func() error
}

func (l *AssetLoader) Add(fn func() error) {
    l.loadFn = append(l.loadFn, fn)
    l.total++
}

func (l *AssetLoader) LoadNext() (bool, error) {
    if l.loaded >= l.total {
        return true, nil
    }
    if err := l.loadFn[l.loaded](); err != nil {
        return false, err
    }
    l.loaded++
    return l.loaded >= l.total, nil
}

func (l *AssetLoader) Progress() float64 {
    if l.total == 0 {
        return 1.0
    }
    return float64(l.loaded) / float64(l.total)
}

func (g *Game) Update() error {
    if g.loadState == LoadingAssets {
        done, err := g.loader.LoadNext()
        if err != nil {
            return err
        }
        g.progress = g.loader.Progress()
        if done {
            g.loadState = LoadingDone
        }
        return nil
    }

    // Normal game update
    return nil
}

func (g *Game) Draw(screen *ebiten.Image) {
    if g.loadState == LoadingAssets {
        ebitenutil.DebugPrintAt(screen,
            fmt.Sprintf("Loading... %d%%", int(g.progress*100)),
            screen.Bounds().Dx()/2-40, screen.Bounds().Dy()/2,
        )
        // Draw progress bar
        barW := 200
        barH := 10
        barX := screen.Bounds().Dx()/2 - barW/2
        barY := screen.Bounds().Dy()/2 + 20
        ebitenutil.DrawRect(screen, barX, barY, barW, barH, color.RGBA{60, 60, 60, 255})
        ebitenutil.DrawRect(screen, barX, barY, int(float64(barW)*g.progress), barH, color.RGBA{0, 200, 0, 255})
        return
    }

    // Normal game draw
}
```

---
