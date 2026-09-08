---
name: resources
description: Ebitengine asset loading, resource management, tilemaps (LDtk, Tiled), Aseprite sprites, embed.FS.
metadata:
  risk: none
  source: official
  date_added: '2026-05-12'
---
# Resources

> Asset loading, resource management, tilemaps, sprite sheets, and save data for Ebitengine.

---

## References

Deep-dive topics are split into focused reference files:

- [Embedding & Loading](references/embedding-loading.md) — covers Embedding Assets with embed.FS, Loading Images, Resource Manager (ebitengine-resource)
- [Sprite Sheets & Tile Maps](references/sprites-tilemaps.md) — covers Sprite Sheets, Tile Maps
- [Procedural Generation & Save Data](references/procedural-saves.md) — covers Procedural Generation, Save Data (gdata)
- [Asset Organization & Loading Screens](references/organization.md) — covers Asset Organization, Loading Screen Pattern

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Use `os.Open()` for game assets | Use `embed.FS` for portability |
| Forget `_ "image/png"` import | Always import required decoder packages |
| Load images in `Update()`/`Draw()` | Load everything at startup or loading screen |
| Store raw `[]byte` alongside `*ebiten.Image` | Load once, discard raw bytes after decode |
| Hard-code file paths | Use constants or config for asset paths |
| Load entire level at once | Stream/load visible chunks for large levels |
| Skip error handling on asset load | Always check errors, fail fast on missing assets |
| Use `gdata` for large binary data | Use `gdata` for save games only, embed other data |
| Embed hundreds of MB of assets | Consider loading screens with chunked loading |
| Ignore LDtk entity fields | Use entity fields for gameplay parameters (spawn points, etc.) |

## When to Use
This skill is applicable when loading, managing, or organizing game assets in an Ebitengine project: images, audio, tilemaps, sprite sheets, or save data.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
