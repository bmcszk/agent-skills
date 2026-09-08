---
name: rendering
description: 'Ebitengine rendering: images, sprites, tilemaps, camera, text, shaders (Kage), DrawImageOptions, GeoM.'
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

- [Images & Drawing](references/images.md) — covers Image Basics, DrawImageOptions, Drawing Primitives
- [Sprites & Tilemaps](references/sprites-tilemaps.md) — covers Sprite Animation, Tilemap Rendering
- [Camera & Text](references/camera-text.md) — covers Camera, Text Rendering
- [Shaders & Off-Screen](references/shaders.md) — covers Shaders (Kage), Off-Screen Buffers

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

## When to Use
This skill is applicable when implementing or modifying rendering in an Ebitengine game: drawing images, sprites, tilemaps, camera, text, or shaders.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
