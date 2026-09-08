---
name: game-loop
description: Ebitengine game loop, ebiten.Game interface, TPS/FPS, window management, RunGameOptions.
metadata:
  risk: none
  source: official
  date_added: '2026-05-12'
---
# Game Loop

> The `ebiten.Game` interface and loop lifecycle.

---

## The Game Interface

Every Ebitengine game implements three methods:

```go
type Game interface {
    Update() error
    Draw(screen *ebiten.Image)
    Layout(outsideWidth, outsideHeight int) (screenWidth, screenHeight int)
}
```

### Update() error

- Called once per tick (1/60s by default, configurable via `ebiten.SetTPS()`)
- All game logic goes here: movement, collision, AI, state transitions
- Return `nil` to continue, return error to exit
- Return `ebiten.Termination` for clean exit without error message

### Draw(screen *ebiten.Image)

- Called once per frame (tied to display refresh rate)
- All rendering goes here: draw images, shapes, text
- **Never modify game state in Draw()** — it may be called at different rates than Update()
- The `screen` parameter is the final render target

### Layout(outsideWidth, outsideHeight int) (int, int)

- Returns the **logical screen size** in pixels
- Engine auto-scales logical screen to window/monitor size
- Return fixed size for pixel-perfect rendering (e.g., `return 320, 240`)
- Return `outsideWidth, outsideHeight` for dynamic/responsive sizing

---

## Starting the Game

```go
func main() {
    ebiten.SetWindowSize(640, 480)
    ebiten.SetWindowTitle("My Game")
    ebiten.SetWindowResizingMode(ebiten.WindowResizingModeEnabled)
    ebiten.SetFPSMode(ebiten.FPSModeVsyncOn)

    if err := ebiten.RunGame(&Game{}); err != nil {
        log.Fatal(err)
    }
}
```

### RunGameOptions (v2.4+)

```go
opts := &ebiten.RunGameOptions{
    GraphicsLibrary: ebiten.GraphicsLibraryOpenGL,
    InitUnfocused:   false,
    ScreenClearedEveryFrame: true,
    SkipTaskbar:     false,
}
ebiten.RunGameWithOptions(&Game{}, opts)
```

---

## Window Configuration

| Function | Purpose |
|----------|---------|
| `SetWindowSize(w, h int)` | Window size in device-independent pixels |
| `SetWindowTitle(title string)` | Window title |
| `SetWindowResizingMode(mode)` | `WindowResizingModeDisabled`, `WindowResizingModeOnlyFullscreenEnabled`, `WindowResizingModeEnabled` |
| `SetWindowDecorated(decorated bool)` | Show/hide title bar |
| `SetWindowPosition(x, y int)` | Window position |
| `SetWindowFloating(float bool)` | Keep window on top |
| `SetWindowMousePassthrough(on bool)` | Click-through window |
| `SetFullscreen(fullscreen bool)` | Toggle fullscreen |
| `SetFPSMode(mode)` | `FPSModeVsyncOn` (default), `FPSModeVsyncOffMaximum`, `FPSModeVsyncOffMinimum` |
| `SetTPS(tps int)` | Ticks per second (default 60) |
| `SetScreenClearedEveryFrame(cleared bool)` | Auto-clear screen before Draw |
| `SetScreenFilterEnabled(enabled bool)` | Enable/disable screen scaling filter |
| `SetVsyncEnabled(enabled bool)` | VSync control |

### Read State

| Function | Returns |
|----------|---------|
| `WindowSize()` | `(w, h int)` |
| `IsFullscreen()` | `bool` |
| `IsWindowDecorated()` | `bool` |
| `WindowPosition()` | `(x, y int)` |
| `CurrentFPS()` | `float64` |
| `CurrentTPS()` | `float64` |
| `ActualFPS()` | `float64` |
| `ActualTPS()` | `float64` |
| `IsFocused()` | `bool` |
| `IsScreenTransparent()` | `bool` |

---

## TPS Modes

```go
ebiten.SetTPS(60)                        // Fixed 60 ticks/sec
ebiten.SetTPS(30)                        // Fixed 30 ticks/sec
ebiten.SetTPS(ebiten.SyncWithFPS)        // Update called every frame (decoupled)
```

### When to use SyncWithFPS

- When you want Update and Draw to be 1:1
- When frame timing matters more than fixed timestep
- Note: game logic becomes frame-rate dependent (less deterministic)

---

## Game State Pattern

```go
type Game struct {
    state  GameState
    player *Player
    level  *Level
    camera *Camera
}

type GameState int

const (
    StateTitle GameState = iota
    StatePlaying
    StatePaused
    StateGameOver
)

func (g *Game) Update() error {
    switch g.state {
    case StateTitle:
        if inpututil.IsKeyJustPressed(ebiten.KeyEnter) {
            g.state = StatePlaying
        }
    case StatePlaying:
        g.player.Update()
        g.level.Update()
        g.camera.Follow(g.player.Position())
    case StatePaused:
        if inpututil.IsKeyJustPressed(ebiten.KeyEscape) {
            g.state = StatePlaying
        }
    case StateGameOver:
        if inpututil.IsKeyJustPressed(ebiten.KeyEnter) {
            g.reset()
            g.state = StateTitle
        }
    }
    return nil
}

func (g *Game) Draw(screen *ebiten.Image) {
    switch g.state {
    case StateTitle:
        // draw title
    case StatePlaying, StatePaused:
        g.camera.Draw(screen, g.level, g.player)
    case StateGameOver:
        // draw game over
    }
}
```

---

## Scene Management

For larger games, use a scene manager instead of switch/case:

| Library | Approach |
|---------|----------|
| [stagehand](https://github.com/joelchutz/stagehand) | Full scene manager with transitions |
| [bamenn](https://github.com/noppikinatta/bamenn) | Simple scene library |

```go
type Scene interface {
    Update() error
    Draw(screen *ebiten.Image)
    Layout(w, h int) (int, int)
}
```

---

## Clean Exit

```go
func (g *Game) Update() error {
    if ebiten.IsKeyPressed(ebiten.KeyEscape) {
        return ebiten.Termination
    }
    return nil
}
```

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Modify state in `Draw()` | All state changes in `Update()` only |
| Allocate in `Update()`/`Draw()` hot paths | Pre-allocate in constructor |
| Ignore `Layout()` consistency | Return same logical size unless intentionally dynamic |
| Use `log.Fatal()` in Update | Return error to let RunGame handle it |
| Block in `Update()` | Keep Update non-blocking, < 16ms per tick |

---

> **Remember:** Update is logic. Draw is rendering. Never mix them.

## When to Use
This skill is applicable when implementing or modifying the Ebitengine game loop, window configuration, or game state management.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
