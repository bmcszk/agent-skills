---
name: audio
description: 'Ebitengine audio: sound effects, music, audio players, streaming, resound effects.'
metadata:
  risk: none
  source: official
  date_added: '2026-05-12'
---
# Audio

> Sound effects, music, and audio playback in Ebitengine.

---

## Audio Context Initialization

Every Ebitengine audio session requires a single `audio.Context`:

```go
import "github.com/hajimehoshi/ebiten/v2/audio"

const sampleRate = 44100

type Game struct {
    audioCtx *audio.Context
}

func NewGame() *Game {
    return &Game{
        audioCtx: audio.NewContext(sampleRate),
    }
}
```

**Rules:**
- Create exactly one `audio.Context` for the entire game
- Create it once at startup (not per frame)
- Sample rate must match your audio files (typically 44100 Hz)

---

## Playing Sounds from WAV/OGG/MP3

### Loading Audio Files

```go
import (
    "bytes"
    "io"

    "github.com/hajimehoshi/ebiten/v2/audio"
    "github.com/hajimehoshi/ebiten/v2/audio/wav"
    "github.com/hajimehoshi/ebiten/v2/audio/vorbis"
    "github.com/hajimehoshi/ebiten/v2/audio/mp3"
)

func loadWAV(audioCtx *audio.Context, data []byte) (*audio.Player, error) {
    return wav.Decode(audioCtx, bytes.NewReader(data))
}

func loadOGG(audioCtx *audio.Context, data []byte) (*audio.Player, error) {
    return vorbis.Decode(audioCtx, bytes.NewReader(data))
}

func loadMP3(audioCtx *audio.Context, data []byte) (*audio.Player, error) {
    return mp3.Decode(audioCtx, bytes.NewReader(data))
}
```

### Decoder Import Table

| Format | Import | Decoder |
|--------|--------|---------|
| WAV | `ebiten/v2/audio/wav` | `wav.Decode()` |
| OGG/Vorbis | `ebiten/v2/audio/vorbis` | `vorbis.Decode()` |
| MP3 | `ebiten/v2/audio/mp3` | `mp3.Decode()` |
| XM | `github.com/quasilyte/xm` | `xm.NewFromData()` |
| Custom PCM | Manual `io.Reader` | `audio.NewPlayer()` |

### Playing a Sound Effect

```go
type Game struct {
    audioCtx  *audio.Context
    jumpSound *audio.Player
}

func NewGame() *Game {
    g := &Game{
        audioCtx: audio.NewContext(44100),
    }

    jumpData, _ := os.ReadFile("assets/jump.wav")
    g.jumpSound, _ = wav.Decode(g.audioCtx, bytes.NewReader(jumpData))

    return g
}

func (g *Game) Update() error {
    if inpututil.IsKeyJustPressed(ebiten.KeySpace) {
        g.playSound(g.jumpSound)
    }
    return nil
}

func (g *Game) playSound(p *audio.Player) {
    p := g.audioCtx.NewPlayerFromBytes(g.audioCtx, p.(interface{ Bytes() []byte }).Bytes())
    p.Play()
}
```

---

## Background Music (Looping)

### Simple Loop

```go
type Game struct {
    audioCtx *audio.Context
    bgm      *audio.Player
}

func NewGame() *Game {
    g := &Game{
        audioCtx: audio.NewContext(44100),
    }

    bgmData, _ := os.ReadFile("assets/music.ogg")
    bgmPlayer, _ := vorbis.Decode(g.audioCtx, bytes.NewReader(bgmData))
    g.bgm = audio.NewInfiniteLoop(bgmPlayer, bgmPlayer.Length())
    g.bgm.Play()

    return g
}
```

### InfiniteLoop

`audio.NewInfiniteLoop` wraps a decoded audio player for seamless looping:

```go
decoded, _ := vorbis.Decode(audioCtx, reader)
loop := audio.NewInfiniteLoop(decoded, decoded.Length())
loop.Play()
```

`NewInfiniteLoop` takes the source player and its total length. It creates a seamlessly looping player.

---

## Audio Pool for Simultaneous Sounds

To play the same sound multiple times simultaneously (e.g., rapid gunfire):

```go
type SoundPool struct {
    audioCtx *audio.Context
    sounds   map[string][]byte
}

func NewSoundPool(audioCtx *audio.Context) *SoundPool {
    return &SoundPool{
        audioCtx: audioCtx,
        sounds:   make(map[string][]byte),
    }
}

func (p *SoundPool) Load(name string, data []byte) {
    p.sounds[name] = data
}

func (p *SoundPool) Play(name string) {
    data, ok := p.sounds[name]
    if !ok {
        return
    }
    player := p.audioCtx.NewPlayerFromBytes(data)
    player.Play()
}
```

### Usage

```go
pool := NewSoundPool(audioCtx)

// Pre-load sounds
jumpData, _ := os.ReadFile("assets/jump.wav")
pool.Load("jump", jumpData)

shootData, _ := os.ReadFile("assets/shoot.wav")
pool.Load("shoot", shootData)

// Play anytime (each call creates a new player)
pool.Play("jump")
pool.Play("shoot")
```

### Limiting Concurrent Sounds

```go
type CappedSoundPool struct {
    audioCtx  *audio.Context
    sounds    map[string][]byte
    active    []*audio.Player
    maxActive int
}

func (p *CappedSoundPool) Play(name string) {
    // Clean up finished players
    alive := p.active[:0]
    for _, player := range p.active {
        if player.IsPlaying() {
            alive = append(alive, player)
        }
    }
    p.active = alive

    if len(p.active) >= p.maxActive {
        return
    }

    data := p.sounds[name]
    player := p.audioCtx.NewPlayerFromBytes(data)
    p.active = append(p.active, player)
    player.Play()
}
```

---

## resound Effects Library

[resound](https://github.com/SolarLune/resound) provides audio effects: delay, low-pass filter, panning, distortion, and more.

```go
import "github.com/SolarLune/resound"

// Create effects chain
delay := resound.NewDelay(audioCtx)
delay.SetDelayTime(0.3)
delay.SetFeedback(0.5)

lowpass := resound.NewFilter(audioCtx)
lowpass.SetType(resound.FilterTypeLowPass)
lowpass.SetCutoff(800)

pan := resound.NewPan(audioCtx)
pan.SetPan(0.5) // -1.0 (left) to 1.0 (right)

// Apply to player
delay.SetSource(bgmPlayer)
lowpass.SetSource(delay)
pan.SetSource(lowpass)
pan.Play()
```

### Available Effects

| Effect | Type | Purpose |
|--------|------|---------|
| `resound.NewDelay()` | Delay/Echo | Echo effect |
| `resound.NewFilter()` | Filter | Low-pass, high-pass, band-pass |
| `resound.NewPan()` | Panning | Stereo positioning |
| `resound.NewDistortion()` | Distortion | Overdrive effect |
| `resound.NewCompressor()` | Compressor | Dynamic range compression |
| `resound.NewReverb()` | Reverb | Room ambiance |

---

## Audio File Format Matrix

| Format | Extension | Pros | Cons | Best For |
|--------|-----------|------|------|----------|
| WAV | `.wav` | Fast decode, no quality loss | Large file size | Short SFX |
| OGG/Vorbis | `.ogg` | Small size, good quality | CPU to decode | Music, long SFX |
| MP3 | `.mp3` | Universal, small | Gap on loop (encoder padding) | Non-looping music |
| XM | `.xm` | Tiny file, procedural | Tracker knowledge needed | Retro music |

### Recommendations

- **Sound effects:** WAV (short) or OGG (long)
- **Background music:** OGG (for looping) or XM (for retro)
- **Avoid MP3 for looping BGM** — encoder padding causes audible gaps

---

## Volume Control

```go
// Set volume (0.0 to 1.0)
player.SetVolume(0.5)

// Master volume pattern
type AudioManager struct {
    masterVolume float64
    sfxVolume    float64
    musicVolume  float64
    audioCtx     *audio.Context
}

func (m *AudioManager) PlaySFX(player *audio.Player) {
    player.SetVolume(m.masterVolume * m.sfxVolume)
    player.Play()
}

func (m *AudioManager) SetMusicVolume(vol float64) {
    m.musicVolume = vol
    if m.currentBGM != nil {
        m.currentBGM.SetVolume(m.masterVolume * m.musicVolume)
    }
}
```

---

## Pausing and Resuming

```go
// Pause
player.Pause()

// Resume
player.Play()

// Check state
player.IsPlaying()

// Seek
player.SetPosition(timeOffset)
```

---

## Audio Guidelines

1. **Load all audio at startup** — never load during gameplay
2. **Use `NewPlayerFromBytes` for SFX** — allows simultaneous playback
3. **Use `InfiniteLoop` for BGM** — seamless looping
4. **Prefer OGG over MP3 for music** — no gap issues on loop
5. **Keep sample rate consistent** — all files at 44100 Hz
6. **Cap concurrent sounds** — too many active players degrades performance
7. **Clean up finished players** — call `Close()` or let GC handle it
8. **Test on target platforms** — audio behavior differs on mobile/WASM

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Create `audio.Context` per frame | Create exactly one at startup |
| Use MP3 for looping BGM | Use OGG/WAV for seamless loops |
| Decode audio in `Update()`/`Draw()` | Decode at load time, store bytes |
| Play raw decoded player for SFX | Use `NewPlayerFromBytes` for each play |
| Ignore `IsPlaying()` cleanup | Close or pool finished players |
| Load large uncompressed WAV for music | Use compressed OGG for long audio |
| Skip audio initialization error checks | Always check errors from `NewContext` |
| Use different sample rates for files | Standardize on 44100 Hz |
| Create new `os.File` reads per play | Read file once, store `[]byte` |

## When to Use
This skill is applicable when implementing or modifying audio in an Ebitengine game: sound effects, background music, audio effects, or resource management.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
