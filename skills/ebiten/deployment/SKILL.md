---
name: deployment
description: 'Ebitengine cross-platform deployment: desktop, WebAssembly, mobile (iOS/Android), Steam, Nintendo Switch.'
metadata:
  risk: none
  source: official
  date_added: '2026-05-12'
---
# Deployment

> Cross-platform builds for Ebitengine games: desktop, web, mobile, consoles.

---

## Supported Platforms

| Platform | Status | Backend |
|----------|--------|---------|
| Windows | Stable | DirectX (default), OpenGL |
| macOS | Stable | Metal (default), OpenGL |
| Linux | Stable | OpenGL |
| WebAssembly | Stable | WebGL |
| Android | Stable | OpenGL ES |
| iOS | Stable | Metal |
| Nintendo Switch | Available via paid license | Proprietary |

---

## Desktop Build

### Basic Build

```bash
# Build for current platform
go build -o game .

# Windows
GOOS=windows GOARCH=amd64 go build -o game.exe .

# macOS
GOOS=darwin GOARCH=amd64 go build -o game .
GOOS=darwin GOARCH=arm64 go build -o game .

# Linux
GOOS=linux GOARCH=amd64 go build -o game .
```

### CGO Dependencies

Ebitengine uses CGO on some platforms:

| Platform | CGO Required | Notes |
|----------|-------------|-------|
| Windows | No | Pure Go with DirectX |
| macOS | Yes | Needs Xcode/Clang |
| Linux | Yes | Needs `gcc`, `libgl1-mesa-dev`, `libxcursor-dev`, `libxrandr-dev`, `libxinerama-dev`, `libxi-dev`, `libxxf86vm-dev`, `libc6-dev` |

### Linux Dependencies

```bash
# Debian/Ubuntu
sudo apt-get install libc6-dev libgl1-mesa-dev libxcursor-dev libxrandr-dev libxinerama-dev libxi-dev libxxf86vm-dev libasound2-dev pkg-config

# Fedora
sudo dnf install mesa-libGL-devel libXcursor-devel libXrandr-devel libXinerama-devel libXi-devel libXxf86vm-devel alsa-lib-devel pkgconfig

# Arch
sudo pacman -S mesa libxcursor libxrandr libxinerama libxi libxxf86vm alsa-lib pkg-config
```

### Windows Cross-Compile from Linux

```bash
GOOS=windows GOARCH=amd64 CGO_ENABLED=1 CC=x86_64-w64-mingw32-gcc go build -o game.exe .
```

### macOS Cross-Compile

Cross-compiling macOS binaries from Linux requires osxcross or similar toolchain. Alternatively, build on macOS directly or use CI.

---

## WebAssembly

### Build

```bash
GOOS=js GOARCH=wasm go build -o game.wasm .
```

### HTML Shell

Create an HTML file to load the WASM module:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>My Game</title>
    <style>
        body { margin: 0; background: #000; }
        canvas { display: block; margin: auto; }
    </style>
</head>
<body>
    <canvas id="game"></canvas>
    <script src="wasm_exec.js"></script>
    <script>
        const go = new Go();
        WebAssembly.instantiateStreaming(
            fetch("game.wasm"), go.importObject
        ).then(result => {
            go.run(result.instance);
        });
    </script>
</body>
</html>
```

Copy `wasm_exec.js` from your Go installation:

```bash
cp "$(go env GOROOT)/misc/wasm/wasm_exec.js" .
```

### wasmserve for Development

```bash
go install github.com/hajimehoshi/wasmserve@latest
wasmserve -http=:8080 .
```

### WASM Considerations

| Aspect | Detail |
|--------|--------|
| Audio | Limited to specific formats; no MP3 in some browsers |
| File system | No direct file access; use `embed.FS` or HTTP fetch |
| Performance | 30-60% of native; heavy shaders may struggle |
| Binary size | Can be large; use `-ldflags="-s -w"` to reduce |
| Gamepad | Supported via standard gamepad API |
| Touch | Supported via touch events |
| Fullscreen | Limited browser support |
| Save data | Use `gdata` library or `localStorage` |

### Optimize WASM Binary

```bash
# Strip debug info
GOOS=js GOARCH=wasm go build -ldflags="-s -w" -o game.wasm .

# Further compress with gzip
gzip -9 -c game.wasm > game.wasm.gz
```

Serve with `Content-Encoding: gzip` for automatic decompression.

---

## Android

### Setup

```bash
# Install ebitenmobile tool
go install github.com/hajimehoshi/ebiten/v2/cmd/ebitenmobile@latest
```

### Build

```bash
# Generate Android library
ebitenmobile bind -target android -o game.aar .

# For use in Android Studio project
```

### Requirements

| Requirement | Detail |
|-------------|--------|
| Android SDK | API level 16+ |
| NDK | Latest recommended |
| Go version | 1.21+ |
| minSdkVersion | 16 |

### Integration with Android Project

1. Run `ebitenmobile bind -target android -o game.aar .`
2. Copy `game.aar` into Android Studio project's `libs/` directory
3. Add to `build.gradle`: `implementation files('libs/game.aar')`
4. Create an `Activity` that launches the Ebiten game view

---

## iOS

### Setup

```bash
go install github.com/hajimehoshi/ebiten/v2/cmd/ebitenmobile@latest
```

### Build

```bash
# Generate iOS framework
ebitenmobile bind -target ios -o Game.xcframework .

# For use in Xcode project
```

### Requirements

| Requirement | Detail |
|-------------|--------|
| Xcode | 14+ |
| macOS | Required for build |
| Go version | 1.21+ |
| Deployment target | iOS 13+ |

### Integration with Xcode Project

1. Run `ebitenmobile bind -target ios -o Game.xcframework .`
2. Drag `Game.xcframework` into Xcode project
3. Create a `UIViewController` that presents the Ebiten view

---

## Mobile Input Considerations

| Desktop Input | Mobile Equivalent |
|---------------|-------------------|
| Keyboard arrows | Touch joystick / swipe |
| Space / Z / X | Tap buttons / multi-touch zones |
| Mouse click | Tap |
| Mouse position | Touch position |
| Escape | Back button / gesture |
| Gamepad | Bluetooth gamepad (supported) |

### Touch Controls Pattern

```go
type TouchButton struct {
    Bounds  image.Rectangle
    Pressed bool
    ID      ebiten.TouchID
}

func (b *TouchButton) Update() {
    b.Pressed = false
    touchIDs := inpututil.AppendJustPressedTouchIDs(nil)
    for _, id := range touchIDs {
        x, y := ebiten.TouchPosition(id)
        if x >= b.Bounds.Min.X && x <= b.Bounds.Max.X &&
            y >= b.Bounds.Min.Y && y <= b.Bounds.Max.Y {
            b.Pressed = true
            b.ID = id
        }
    }
}
```

---

## Steam Integration

```go
import "github.com/hajimehoshi/go-steamworks"

func init() {
    steamworks.Init()
}

func (g *Game) Update() error {
    steamworks.Update()

    // Achievements
    steamworks.SetAchievement("first_win")
    steamworks.StoreStats()

    // Leaderboards
    steamworks.UploadLeaderboardScore("high_score", score)

    return nil
}
```

Requires Steamworks SDK installed. Only works when launched through Steam.

---

## Build Optimization

### Binary Size

```bash
# Strip symbols
go build -ldflags="-s -w" -o game .

# With UPX compression (optional, may trigger antivirus)
upx --best game
```

### Embed Assets

```go
//go:embed assets/*
var assets embed.FS
```

Using `embed.FS` eliminates external file dependencies and simplifies deployment.

### Build Tags

```go
// +build !mobile

package main

// Desktop-only code

// +build mobile

package main

// Mobile-specific code
```

---

## CI/CD GitHub Actions

```yaml
name: Build

on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - name: Install Linux dependencies
        if: runner.os == 'Linux'
        run: |
          sudo apt-get update
          sudo apt-get install -y libgl1-mesa-dev libxcursor-dev libxrandr-dev libxinerama-dev libxi-dev libxxf86vm-dev libasound2-dev pkg-config
      - name: Build
        run: go build -ldflags="-s -w" -o game .

  wasm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - name: Build WASM
        run: GOOS=js GOARCH=wasm go build -ldflags="-s -w" -o game.wasm .
      - uses: actions/upload-artifact@v4
        with:
          name: wasm-build
          path: game.wasm

  release:
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    needs: [build, wasm]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - name: Build all platforms
        run: |
          GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o game-windows-amd64.exe .
          GOOS=darwin GOARCH=arm64 go build -ldflags="-s -w" -o game-darwin-arm64 .
          GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o game-linux-amd64 .
          GOOS=js GOARCH=wasm go build -ldflags="-s -w" -o game.wasm .
      - uses: softprops/action-gh-release@v1
        with:
          files: |
            game-windows-amd64.exe
            game-darwin-arm64
            game-linux-amd64
            game.wasm
```

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Read files with `os.Open()` at runtime | Use `embed.FS` for portable assets |
| Hard-code file paths | Use `embed.FS` or relative paths from executable |
| Test only on your dev platform | Set up CI for all target platforms |
| Skip mobile-specific input handling | Add touch controls for mobile targets |
| Use CGO-dependent libraries for WASM | Stick to pure Go for WASM compatibility |
| Ignore WASM binary size | Strip with `-ldflags="-s -w"` and gzip |
| Use `os.ReadFile()` for assets | Use `embed.FS` or resource manager |
| Assume desktop resolutions | Handle dynamic layouts in `Layout()` |
| Skip testing audio on mobile/WASM | Test audio on each target platform |

## When to Use
This skill is applicable when building, packaging, or deploying an Ebitengine game for any platform: desktop, web, mobile, or console.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
