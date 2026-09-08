# Embedding & Loading

## Embedding Assets with embed.FS

```go
import "embed"

//go:embed assets/images/*.png
var imagesFS embed.FS

//go:embed assets/audio/*.wav
var audioFS embed.FS

//go:embed assets/**
var assetsFS embed.FS
```

### Loading from embed.FS

```go
func loadEmbeddedImage(fs embed.FS, path string) (*ebiten.Image, error) {
    data, err := fs.ReadFile(path)
    if err != nil {
        return nil, err
    }
    img, _, err := image.Decode(bytes.NewReader(data))
    if err != nil {
        return nil, err
    }
    return ebiten.NewImageFromImage(img), nil
}
```

### Required Decoder Imports

```go
import (
    _ "image/png"  // Required for PNG decoding
    _ "image/jpeg" // Required for JPEG decoding
)
```

Without these blank imports, `image.Decode` will fail with "unknown format".

---

## Loading Images

### Single Image

```go
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

### Batch Loading

```go
type AssetStore struct {
    images map[string]*ebiten.Image
}

func (s *AssetStore) LoadDirectory(fs embed.FS, dir string, exts ...string) error {
    entries, err := fs.ReadDir(dir)
    if err != nil {
        return err
    }
    for _, entry := range entries {
        if entry.IsDir() {
            continue
        }
        name := entry.Name()
        for _, ext := range exts {
            if strings.HasSuffix(name, ext) {
                img, err := loadEmbeddedImage(fs, path.Join(dir, name))
                if err != nil {
                    return fmt.Errorf("load %s: %w", name, err)
                }
                s.images[name] = img
                break
            }
        }
    }
    return nil
}

func (s *AssetStore) Get(name string) *ebiten.Image {
    return s.images[name]
}
```

---

## Resource Manager (ebitengine-resource)

```go
import "github.com/quasilyte/ebitengine-resource"

type res struct {
    PlayerImage resource.ResourceID
    EnemyImage  resource.ResourceID
    JumpSound   resource.ResourceID
}

var resources = res{
    PlayerImage: 1,
    EnemyImage:  2,
    JumpSound:   3,
}

type game struct {
    rm *resource.Manager
}

func newGame() *game {
    rm := resource.NewManager()
    g := &game{rm: rm}

    rm.RegisterImage(resources.PlayerImage, "assets/player.png")
    rm.RegisterImage(resources.EnemyImage, "assets/enemy.png")
    rm.RegisterAudio(resources.JumpSound, "assets/jump.wav")

    return g
}

func (g *game) LoadResources() error {
    g.rm.LoadAll(func(err error, id resource.ResourceID) {
        if err != nil {
            log.Printf("failed to load resource %d: %v", id, err)
        }
    })
    return nil
}
```

---
