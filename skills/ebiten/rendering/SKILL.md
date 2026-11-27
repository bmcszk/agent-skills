---
name: rendering
description: 'Use when rendering in Ebitengine: images, sprites, tilemaps, camera, text, shaders (Kage), DrawImageOptions, GeoM.'
metadata:
  risk: none
  source: official
  date_added: '2026-05-12'
---
# Rendering

> Images, sprites, tilemaps, camera, text, and shaders in Ebitengine.

---

## References

Deep-dive topics are split into focused reference files:

- [Images & Drawing](references/images.md) - covers Image Basics, DrawImageOptions, Drawing Primitives
- [Sprites & Tilemaps](references/sprites-tilemaps.md) - covers Sprite Animation, Tilemap Rendering
- [Camera & Text](references/camera-text.md) - covers Camera, Text Rendering
- [Shaders & Off-Screen](references/shaders.md) - covers Shaders (Kage), Off-Screen Buffers

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Call `ebiten.NewImage()` in `Draw()` | Pre-allocate in constructor or load phase |
| Create `*ebiten.DrawImageOptions` every frame | Reuse and call `GeoM.Reset()` |
| Draw all tiles even if off-screen | Implement camera culling (only draw visible tiles) |
| Use `ebitenutil.DebugPrint` in production | Use etxt or bitmapfont for real text rendering |
| Forget to `Clear()` off-screen buffers | Clear before drawing to them |
| Use `FilterLinear` for pixel art | Use `FilterNearest` for crisp pixel art |
| Apply transforms without considering order | Remember: transforms apply in reverse call order |
| Load/decode images every frame | Load once, cache the `*ebiten.Image` |
| Use `screen.Set(x, y, color)` for many pixels | Use shaders or `Image.Fill()` for bulk pixel ops |
| Call `Target().ReadPixels()` outside a running game loop | `ReadPixels` panics unless `ebiten.RunGame` is running - the `//go:build windowed` tag is necessary but NOT sufficient; read from the `screen` image passed into `Draw`, or produce test pixels headlessly through your own frame/palette expansion seam |

## Windowed build tags and pixel reads

- `//go:build windowed` controls COMPILATION only - it never initializes ebiten's
  UI backend; the backend's `running` state is set solely inside `ebiten.RunGame`.
- A pixel-reading test must either run inside a real loop (an app hosts exactly one
  run loop per process) or stay headless: produce expected pixels through your own
  palette/frame expansion seam and assert on those.
- Gate the loop-driven capture on the display being available; it skips on CI and
  headless machines, so never let it be the only coverage for a capture path.
