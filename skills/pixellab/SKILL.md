---
name: pixellab
description: 'AI-powered pixel art generation for characters, animations, tiles, and game assets via PixelLab (mcpc). Use when you need character sprites with directional views, animations, isometric tiles, top-down tilesets, sidescroller tilesets, or map objects. All operations are non-blocking and return job IDs for status tracking. Keywords: pixel art, sprite generation, character animation, tileset, isometric tiles, game assets, pixellab.'
license: MIT
metadata:
  audience: developers
  workflow: creative
  category: game-development
  technologies: mcpc, pixellab, pixel-art, game-assets
---

## What this does

Generates AI-powered pixel art including characters with directional views, character animations, isometric tiles, top-down tilesets, sidescroller tilesets, and map objects. All operations are non-blocking and return job IDs for status tracking.

Requires PixelLab subscription with credit fallback support.

## Setup

```bash
mcpc connect ~/.mcpc/mcp.json:pixellab @pixellab
```

## Tools

### Characters

| Tool | Description |
|------|-------------|
| `create_character` | Generate a character from description |
| `get_character` | Get character by ID (read-only) |
| `list_characters` | List all characters (read-only) |
| `animate_character` | Animate an existing character |
| `delete_character` | Delete a character (destructive) |

### Isometric tiles

| Tool | Description |
|------|-------------|
| `create_isometric_tile` | Generate isometric tile from description |
| `get_isometric_tile` | Get tile by ID (read-only) |
| `list_isometric_tiles` | List all isometric tiles (read-only) |
| `delete_isometric_tile` | Delete a tile (destructive) |

### Top-down tilesets

| Tool | Description |
|------|-------------|
| `create_topdown_tileset` | Generate top-down tileset with lower/upper layer descriptions |
| `get_topdown_tileset` | Get tileset by ID (read-only) |
| `list_topdown_tilesets` | List all top-down tilesets (read-only) |
| `delete_topdown_tileset` | Delete a tileset (destructive) |

### Sidescroller tilesets

| Tool | Description |
|------|-------------|
| `create_sidescroller_tileset` | Generate sidescroller/platformer tileset |
| `get_sidescroller_tileset` | Get tileset by ID (read-only) |
| `list_sidescroller_tilesets` | List all sidescroller tilesets (read-only) |
| `delete_sidescroller_tileset` | Delete a tileset (destructive) |

### Objects

| Tool | Description |
|------|-------------|
| `create_object` | Generate an object sprite from description |
| `create_map_object` | Generate a map-scale object |
| `get_object` | Get object by ID (read-only) |
| `list_objects` | List all objects (read-only) |
| `animate_object` | Animate an existing object |
| `vary_object` | Create a variation of an existing object |
| `select_object_frames` | Select specific frames from an object |
| `dismiss_review` | Dismiss review state (destructive) |
| `delete_object` | Delete an object (destructive) |

### Tiles Pro

| Tool | Description |
|------|-------------|
| `create_tiles_pro` | Generate advanced tiles with more options |
| `get_tiles_pro` | Get tile by ID (read-only) |
| `list_tiles_pro` | List all tiles pro (read-only) |
| `delete_tiles_pro` | Delete a tile (destructive) |

## Workflow

### Create and retrieve

```bash
1. mcpc @pixellab tools-call create_character description:="a knight with silver armor"
   # → returns job ID / asset ID
2. mcpc @pixellab tools-call get_character character_id:=<id> → check result / retrieve asset
```

### Animate a character

```bash
1. mcpc @pixellab tools-call create_character description:="a wizard with blue robe" → character_id
2. mcpc @pixellab tools-call animate_character character_id:=<id> action_description:="casting a spell"
   # → animated character
```

### Build a tileset

```bash
1. mcpc @pixellab tools-call create_topdown_tileset lower_description:="grass field" upper_description:="forest with trees"
   # → tileset with transitions
```

## Best practices

- Be descriptive in `description` fields — include style, color, perspective, size
- Use `mcpc @pixellab tools-call get_<type>` to poll for completion on long-running jobs
- Use `mcpc @pixellab tools-call list_<type>` to check existing assets before creating duplicates
- `delete_<type>` requires `confirm:=true` for safety
- All create operations consume credits — use `list_*` first to avoid waste
