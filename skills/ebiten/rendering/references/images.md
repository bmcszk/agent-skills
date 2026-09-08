# Images & Drawing

## Image Basics

### Creating Images

```go
// Empty image (transparent)
img := ebiten.NewImage(64, 64)

// From Go standard image
goImg := /* image.Image */
img := ebiten.NewImageFromImage(goImg)

// Sub-image (zero-copy region from sprite sheet)
region := sheet.SubImage(image.Rect(0, 0, 32, 32)).(*ebiten.Image)
```

### Loading Images from Files

```go
import (
    "image"
    _ "image/png"
    "os"
)

func loadImage(path string) (*ebiten.Image, error) {
    f, err := os.Open(path)
    if err != nil {
        return nil, err
    }
    defer f.Close()
    img, _, err := image.Decode(f)
    if err != nil {
        return nil, err
    }
    return ebiten.NewImageFromImage(img), nil
}
```

For JPEG support, also import `_ "image/jpeg"`.

### SubImage for Sprite Sheets

```go
// Sprite sheet with 32x32 sprites in a grid
func getSprite(sheet *ebiten.Image, col, row int) *ebiten.Image {
    x := col * spriteWidth
    y := row * spriteHeight
    return sheet.SubImage(image.Rect(x, y, x+spriteWidth, y+spriteHeight)).(*ebiten.Image)
}
```

`SubImage` is zero-copy — it references the same pixel data.

---

## DrawImageOptions

`ebiten.DrawImageOptions` controls how images are drawn:

```go
opts := &ebiten.DrawImageOptions{}
opts.GeoM.Translate(100, 200)
opts.GeoM.Scale(2, 2)
screen.DrawImage(sprite, opts)
```

### GeoM (Geometric Transform)

The `GeoM` is a 2D affine transformation matrix:

| Method | Purpose |
|--------|---------|
| `Translate(tx, ty float64)` | Move by offset |
| `Scale(sx, sy float64)` | Scale (1.0 = original) |
| `Rotate(theta float64)` | Rotate (radians, clockwise) |
| `SetTransform(tx, ty, rx, ry float64)` | Combined scale+rotate |
| `Reset()` | Reset to identity |

### Transform Order Matters

Transforms are applied in reverse order (bottom-up matrix multiplication):

```go
opts.GeoM.Translate(-hw, -hh)   // 3. offset back
opts.GeoM.Rotate(angle)          // 2. rotate
opts.GeoM.Translate(hw, hh)      // 1. center origin
opts.GeoM.Translate(x, y)        // 0. world position
```

To rotate around center: translate to origin, rotate, translate back.

### Reusing Options

```go
// Allocate once
opts := &ebiten.DrawImageOptions{}

// Reset each frame
func (g *Game) Draw(screen *ebiten.Image) {
    opts.GeoM.Reset()
    opts.GeoM.Translate(g.player.X, g.player.Y)
    screen.DrawImage(g.player.Sprite, opts)

    opts.GeoM.Reset()
    opts.GeoM.Translate(g.enemy.X, g.enemy.Y)
    screen.DrawImage(g.enemy.Sprite, opts)
}
```

### ColorScale (Tinting & Alpha)

```go
// Make semi-transparent
opts.ColorScale.ScaleAlpha(0.5)

// Tint red (multiply channels)
opts.ColorScale.ScaleR(1.0)
opts.ColorScale.ScaleG(0.0)
opts.ColorScale.ScaleB(0.0)

// Flash white (additive approach via ColorM)
opts.ColorM.Translate(0.5, 0.5, 0.5, 0)

// Full opacity (default)
opts.ColorScale.ScaleAlpha(1.0)
```

### Blend Modes

```go
opts.Blend = ebiten.BlendCopy           // Replace destination
opts.Blend = ebiten.BlendSourceOver     // Alpha blend (default)
opts.Blend = ebiten.BlendAdd            // Additive blending
opts.Blend = ebiten.BlendLighter        // Lighter compositing
```

### Filter Mode

```go
opts.Filter = ebiten.FilterNearest   // Pixel-perfect (default)
opts.Filter = ebiten.FilterLinear    // Smooth interpolation
```

Use `FilterNearest` for pixel art, `FilterLinear` for smooth sprites.

---

## Drawing Primitives

Ebitengine has no built-in primitive drawing. Use ebitenutil or custom functions:

```go
import "github.com/hajimehoshi/ebiten/v2/ebitenutil"

// Line
ebitenutil.DrawLine(screen, x1, y1, x2, y2, color.White)

// Rect outline
ebitenutil.DrawRect(screen, x, y, w, h, color.White)

// Filled rect
img := ebiten.NewImage(w, h)
img.Fill(color.RGBA{255, 0, 0, 255})
screen.DrawImage(img, opts)
```

### Circle (Custom)

```go
func drawCircle(screen *ebiten.Image, cx, cy, r float64, clr color.Color) {
    img := ebiten.NewImage(int(r*2+2), int(r*2+2))
    for angle := 0.0; angle < 360.0; angle += 1.0 {
        rad := angle * math.Pi / 180
        x := int(r + math.Cos(rad)*r)
        y := int(r + math.Sin(rad)*r)
        img.Set(x, y, clr)
    }
    opts := &ebiten.DrawImageOptions{}
    opts.GeoM.Translate(cx-r, cy-r)
    screen.DrawImage(img, opts)
}
```

---
