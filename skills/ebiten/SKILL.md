---
name: ebiten
description: Ebitengine (Ebiten v2) 2D game development in Go. Game loop, input, rendering, ECS, physics, audio, deployment.
metadata:
  risk: none
  source: official
  date_added: '2026-05-12'
---
# Ebitengine (Ebiten v2)

> **Go 2D game engine skill** — covers the full Ebitengine API and ecosystem. Routes to sub-skills by domain.

Ebitengine is a dead simple 2D game library for Go. Cross-platform: desktop (Windows/macOS/Linux), mobile (iOS/Android), WebAssembly, and Nintendo Switch.

**Import:** `github.com/hajimehoshi/ebiten/v2`

---

## When to Use This Skill

You are building a 2D game or interactive graphical application in Go using Ebitengine (Ebiten v2).

---

## Sub-Skill Routing

| If you need... | Use Sub-Skill |
|----------------|---------------|
| Game loop, `ebiten.Game` interface, TPS/FPS, window config | `ebiten/game-loop` |
| Keyboard, mouse, gamepad, touch input | `ebiten/input` |
| Images, sprites, tiles, camera, shaders, text | `ebiten/rendering` |
| Entity Component System (Donburi, Ark, etc.) | `ebiten/ecs` |
| Collision detection, physics, pathfinding | `ebiten/physics` |
| Sound effects, music, audio playback | `ebiten/audio` |
| WASM, mobile, Steam, cross-platform build | `ebiten/deployment` |
| Asset loading, tilemaps (LDtk, Tiled), resource management | `ebiten/resources` |

---

## Minimal Game Template

```go
package main

import (
	"log"

	"github.com/hajimehoshi/ebiten/v2"
)

type Game struct{}

func (g *Game) Update() error {
	return nil
}

func (g *Game) Draw(screen *ebiten.Image) {
}

func (g *Game) Layout(outsideWidth, outsideHeight int) (screenWidth, screenHeight int) {
	return 320, 240
}

func main() {
	ebiten.SetWindowSize(640, 480)
	ebiten.SetWindowTitle("Title")
	if err := ebiten.RunGame(&Game{}); err != nil {
		log.Fatal(err)
	}
}
```

---

## Ecosystem Libraries

### Architecture

| Library | Purpose | Stars |
|---------|---------|-------|
| [donburi](https://github.com/yohamta/donburi) | ECS for Ebitengine | 500+ |
| [ark](https://github.com/mlange-42/ark) | Archetype-based ECS | 400+ |
| [mizu](https://github.com/sedyh/mizu) | ECS framework | 400+ |
| [ebiten-extended](https://github.com/LuigiVanacore/ebiten_extended) | Godot-inspired scene graph, camera, sprites | 100+ |

### GUI

| Library | Purpose |
|---------|---------|
| [ebitenui](https://github.com/ebitenui/ebitenui) | Full widget library (buttons, lists, combo boxes) |
| [furex](https://github.com/yohamta/furex) | Flexbox-based UI framework |
| [etk](https://codeberg.org/tslocum/etk) | Toolkit for graphical interfaces |

### Graphics & Animation

| Library | Purpose |
|---------|---------|
| [ganim8](https://github.com/yohamta/ganim8) | Animation library inspired by anim8 |
| [aseprite](https://github.com/setanarut/aseprite) | Aseprite file parser (layers, tags, slices) |
| [aseplayer](https://github.com/setanarut/aseplayer) | Aseprite animation player |
| [etxt](https://github.com/tinne26/etxt) | Font management and text rendering |
| [colorgrad](https://github.com/mazznoer/colorgrad) | Color scales for data viz and games |
| [tetra3d](https://github.com/SolarLune/tetra3d) | 3D software renderer via Ebitengine |

### Physics & Collision

| Library | Purpose |
|---------|---------|
| [resolv](https://github.com/SolarLune/resolv) | 2D collision detection and resolution |
| [cp](https://github.com/jakecoffman/cp) | Chipmunk2D physics port |
| [box2d-go](https://github.com/oliverbestmann/box2d-go) | Box2D v3 physics port |
| [coll](https://github.com/setanarut/coll) | 2D collision detection |

### World & Maps

| Library | Purpose |
|---------|---------|
| [ldtkgo](https://github.com/SolarLune/ldtkgo) | LDtk level designer loader |
| [go-tiled](https://github.com/lafriks/go-tiled) | Tiled map editor (TMX) parser |
| [dngn](https://github.com/SolarLune/dngn) | Random map generation |
| [paths](https://github.com/SolarLune/paths) | A* pathfinding |

### Input

| Library | Purpose |
|---------|---------|
| [ebitengine-input](https://github.com/quasilyte/ebitengine-input) | Godot-inspired action input system |

### Audio

| Library | Purpose |
|---------|---------|
| [resound](https://github.com/SolarLune/resound) | Sound effects (delay, low-pass, panning, distortion) |
| [xm](https://github.com/quasilyte/xm) | XM music format playback |

### Resources & Tools

| Library | Purpose |
|---------|---------|
| [ebitengine-resource](https://github.com/quasilyte/ebitengine-resource) | Resource manager |
| [gdata](https://github.com/quasilyte/gdata) | Cross-platform gamedata storage |
| [kamera](https://github.com/setanarut/kamera) | Camera with shake, lerp, zoom |

### Networking

| Library | Purpose |
|---------|---------|
| [necs](https://github.com/leap-fish/necs) | Networking layer for Donburi ECS |

### Integration

| Library | Purpose |
|---------|---------|
| [go-steamworks](https://github.com/hajimehoshi/go-steamworks) | Steamworks SDK binding |

---

## Key Concepts

### TPS vs FPS

- **TPS (Ticks Per Second):** How often `Update()` is called. Default: 60. Set via `ebiten.SetTPS()`.
- **FPS (Frames Per Second):** How often `Draw()` is called. Tied to monitor refresh rate.
- `ebiten.CurrentTPS()` / `ebiten.CurrentFPS()` for monitoring.
- Use `ebiten.SetTPS(ebiten.SyncWithFPS)` to decouple update from render.

### Coordinate System

- Origin (0,0) is top-left
- X increases right, Y increases down
- `Layout()` defines logical screen size; engine scales to window

### Image Model

- `ebiten.Image` is the core drawing surface
- `screen` parameter in `Draw()` is the final render target
- Use `SubImage()` for sprite sheet regions (zero-copy)
- Use `ebiten.NewImage()` for off-screen buffers

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Call `ebiten.NewImage()` in `Update()`/`Draw()` | Create images once in `NewGame()` or load phase |
| Use floating-point for pixel positions | Use `float64` with `GeoM` (engine handles sub-pixel) |
| Load assets in `Draw()` | Load in `init()` or dedicated load phase |
| Ignore `Layout()` return values | Return consistent logical size |
| Use `ebiten.IsKeyPressed()` for single actions | Use `inpututil.IsKeyJustPressed()` for one-shot triggers |
| Create `*ebiten.DrawImageOptions` each frame | Reuse and reset with `opts.GeoM.Reset()` |
| Mix game state with rendering logic | Keep `Update()` pure logic, `Draw()` pure rendering |

---

## References

- **Docs:** https://ebitengine.org/en/documents/
- **Cheat Sheet:** https://ebitengine.org/en/documents/cheatsheet.html
- **Examples:** https://github.com/hajimehoshi/ebiten/tree/main/examples
- **Awesome List:** https://github.com/sedyh/awesome-ebitengine
- **Kage Shaders:** https://ebitengine.org/en/documents/shader.html
- **TPS vs FPS:** https://github.com/tinne26/tps-vs-fps

---

> **Remember:** Ebitengine is intentionally simple. Start with the `Game` interface, add libraries only when needed.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
