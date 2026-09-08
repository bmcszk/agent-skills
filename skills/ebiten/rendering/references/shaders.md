# Shaders & Off-Screen

## Shaders (Kage)

Ebitengine uses its own shader language called Kage (Go-like GLSL):

### Basic Shader

```go
// Red tint shader
//go:embed shader.kage
var shaderBytes []byte

shader, err := ebiten.NewShader(shaderBytes)
```

`shader.kage`:
```glsl
package main

func Fragment(position vec4, texCoord vec2, color vec4) vec4 {
    clr := imageSrc0UnsafeAt(texCoord)
    return vec4(clr.r * 1.5, clr.g * 0.5, clr.b * 0.5, clr.a)
}
```

### DrawRectShaderOptions

```go
opts := &ebiten.DrawRectShaderOptions{}
opts.Images[0] = sourceImage
opts.Uniforms = map[string]interface{}{
    "Time": float32(time),
}
screen.DrawRectShader(w, h, shader, opts)
```

### Common Shader Effects

```glsl
// Grayscale
func Fragment(position vec4, texCoord vec2, color vec4) vec4 {
    c := imageSrc0UnsafeAt(texCoord)
    gray := c.r*0.299 + c.g*0.587 + c.b*0.114
    return vec4(gray, gray, gray, c.a)
}

// Invert
func Fragment(position vec4, texCoord vec2, color vec4) vec4 {
    c := imageSrc0UnsafeAt(texCoord)
    return vec4(1.0 - c.r, 1.0 - c.g, 1.0 - c.b, c.a)
}

// Dissolve with uniform threshold
var Threshold float

func Fragment(position vec4, texCoord vec2, color vec4) vec4 {
    c := imageSrc0UnsafeAt(texCoord)
    noise := fract(sin(dot(texCoord, vec2(12.9898, 78.233))) * 43758.5453)
    if noise < Threshold {
        return vec4(0.0)
    }
    return c
}

// Wave distortion with uniform Time
var Time float

func Fragment(position vec4, texCoord vec2, color vec4) vec4 {
    offset := vec2(sin(texCoord.y*10.0 + Time)*0.01, 0.0)
    return imageSrc0UnsafeAt(texCoord + offset)
}
```

### Passing Uniforms

```go
opts.Uniforms = map[string]interface{}{
    "Time":      float32(g.time),
    "Threshold": float32(0.5),
    "Color":     []float32{1.0, 0.0, 0.0, 1.0},
}
```

Uniform types: `float32`, `[]float32` (vec2=2, vec3=3, vec4=4), arrays of these.

---

## Off-Screen Buffers

Use off-screen images for post-processing, lighting, or render layers:

```go
type Game struct {
    lightBuffer *ebiten.Image
    gameBuffer  *ebiten.Image
}

func NewGame() *Game {
    return &Game{
        lightBuffer: ebiten.NewImage(320, 240),
        gameBuffer:  ebiten.NewImage(320, 240),
    }
}

func (g *Game) Draw(screen *ebiten.Image) {
    g.gameBuffer.Clear()
    drawWorld(g.gameBuffer)

    g.lightBuffer.Clear()
    drawLights(g.lightBuffer)

    // Composite
    screen.DrawImage(g.gameBuffer, nil)
    opts := &ebiten.DrawImageOptions{}
    opts.Blend = ebiten.BlendAdd
    opts.ColorScale.ScaleAlpha(0.7)
    screen.DrawImage(g.lightBuffer, opts)
}
```

---
