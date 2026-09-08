# Camera & Text

## Camera

### Basic Follow Camera

```go
type Camera struct {
    X, Y       float64
    Width      int
    Height     int
    WorldW     int
    WorldH     int
}

func (c *Camera) Follow(targetX, targetY float64) {
    c.X = targetX - float64(c.Width)/2
    c.Y = targetY - float64(c.Height)/2
    c.X = math.Max(0, math.Min(c.X, float64(c.WorldW-c.Width)))
    c.Y = math.Max(0, math.Min(c.Y, float64(c.WorldH-c.Height)))
}

func (c *Camera) Offset() (float64, float64) {
    return -c.X, -c.Y
}
```

### kamera Library

```go
import "github.com/setanarut/kamera"

cam := kamera.NewCamera(0, 0, 640, 480)
cam.SmoothFollow = true
cam.LookAt(player.X, player.Y)
cam.Shake(10, 20)
cam.ZoomTo(2.0)

// In Draw
cam.LookAt(player.X, player.Y)
cam.Draw(world, screen)
```

### Screen Shake Pattern

```go
type ScreenShake struct {
    intensity float64
    duration  int
    timer     int
}

func (s *ScreenShake) Trigger(intensity float64, frames int) {
    s.intensity = intensity
    s.duration = frames
    s.timer = frames
}

func (s *ScreenShake) Offset() (float64, float64) {
    if s.timer <= 0 {
        return 0, 0
    }
    s.timer--
    ox := (rand.Float64()*2 - 1) * s.intensity * (float64(s.timer) / float64(s.duration))
    oy := (rand.Float64()*2 - 1) * s.intensity * (float64(s.timer) / float64(s.duration))
    return ox, oy
}
```

---

## Text Rendering

### Debug Text

```go
import "github.com/hajimehoshi/ebiten/v2/ebitenutil"

ebitenutil.DebugPrint(screen, "Hello World")
ebitenutil.DebugPrintAt(screen, fmt.Sprintf("Score: %d", score), 10, 10)
```

Built-in debug font, white text. Only for development/debugging.

### etxt Library

```go
import "github.com/tinne26/etxt"

renderer := etxt.NewStdRenderer()
renderer.SetFont(myFont)
renderer.SetSize(16)
renderer.SetAlign(etxt.YCenter, etxt.XCenter)
renderer.SetTarget(screen)

renderer.Draw("Hello", x, y)
```

### bitmapfont

```go
import "github.com/hajimehoshi/bitmapfont/v3"

text.Draw(screen, "Hello", bitmapfont.Face, x, y, color.White)
```

Using `golang.org/x/image/font` and `golang.org/x/image/math/fixed`:

```go
import (
    "golang.org/x/image/font"
    "golang.org/x/image/font/opentype"
)

func loadFont(data []byte, size float64) (font.Face, error) {
    f, err := opentype.Parse(data)
    if err != nil {
        return nil, err
    }
    return opentype.NewFace(f, &opentype.FaceOptions{
        Size:    size,
        DPI:     72,
        Hinting: font.HintingFull,
    })
}
```

---
