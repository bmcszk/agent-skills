---
name: input
description: 'Ebitengine input handling: keyboard, mouse, gamepad, touch, inpututil for just-pressed detection.'
metadata:
  risk: none
  source: official
  date_added: '2026-05-12'
---
# Input

> Keyboard, mouse, gamepad, and touch input in Ebitengine.

---

## Input API Decision Matrix

| You want... | Use |
|-------------|-----|
| Continuous hold (movement, steering) | `ebiten.IsKeyPressed()` |
| Single press (jump, shoot, menu select) | `inpututil.IsKeyJustPressed()` |
| Single release (charge attack release) | `inpututil.IsKeyJustReleased()` |
| All currently held keys | `ebiten.AppendPressedKeys()` |
| Mouse position | `ebiten.CursorPosition()` |
| Continuous mouse button hold | `ebiten.IsMouseButtonPressed()` |
| Single mouse click | `inpututil.IsMouseButtonJustPressed()` |
| Mouse wheel / scroll | `ebiten.Wheel()` |
| Gamepad button hold | `ebiten.IsStandardGamepadButtonPressed()` |
| Gamepad analog stick | `ebiten.StandardGamepadAxisValue()` |
| Touch press | `inpututil.AppendJustPressedTouchIDs()` |
| Touch position | `ebiten.TouchPosition()` |

---

## Keyboard

### Continuous Input (Held Keys)

Use for movement, holding a direction, charging:

```go
func (g *Game) Update() error {
    speed := 3.0
    if ebiten.IsKeyPressed(ebiten.KeyArrowRight) {
        g.player.X += speed
    }
    if ebiten.IsKeyPressed(ebiten.KeyArrowLeft) {
        g.player.X -= speed
    }
    if ebiten.IsKeyPressed(ebiten.KeyArrowUp) {
        g.player.Y -= speed
    }
    if ebiten.IsKeyPressed(ebiten.KeyArrowDown) {
        g.player.Y += speed
    }
    return nil
}
```

### One-Shot Input (Just Pressed)

Use for jumping, shooting, toggling, menu selection. Requires `inpututil` package:

```go
import "github.com/hajimehoshi/ebiten/v2/inpututil"

func (g *Game) Update() error {
    if inpututil.IsKeyJustPressed(ebiten.KeySpace) {
        g.player.Jump()
    }
    if inpututil.IsKeyJustPressed(ebiten.KeyEnter) {
        g.menu.Select()
    }
    if inpututil.IsKeyJustPressed(ebiten.KeyP) {
        g.paused = !g.paused
    }
    return nil
}
```

### Just Released

```go
if inpututil.IsKeyJustReleased(ebiten.KeySpace) {
    g.player.StopJump()
}
```

### All Pressed Keys

```go
pressedKeys := inpututil.AppendPressedKeys(nil)
for _, key := range pressedKeys {
    // handle each key
}
```

### Key Constants

Common keys in `ebiten` package:

| Constant | Key |
|----------|-----|
| `KeyArrowUp/Down/Left/Right` | Arrow keys |
| `KeySpace` | Space |
| `KeyEnter` | Enter |
| `KeyEscape` | Escape |
| `KeyShiftLeft/ShiftRight` | Shift |
| `KeyControlLeft/ControlRight` | Control |
| `KeyA` through `KeyZ` | Letter keys |
| `Key0` through `Key9` | Number keys |
| `KeyTab` | Tab |
| `KeyBackspace` | Backspace |

---

## Mouse

### Position

```go
mx, my := ebiten.CursorPosition()
```

Returns position in logical screen coordinates (respects `Layout()`).

### Button State

```go
// Continuous hold (drag, aim)
if ebiten.IsMouseButtonPressed(ebiten.MouseButtonLeft) {
    g.player.Shoot()
}

// Single click
if inpututil.IsMouseButtonJustPressed(ebiten.MouseButtonRight) {
    g.player.Dash()
}

// Release
if inpututil.IsMouseButtonJustReleased(ebiten.MouseButtonLeft) {
    g.player.StopShoot()
}
```

### Mouse Buttons

| Constant | Button |
|----------|--------|
| `MouseButtonLeft` | Left click |
| `MouseButtonRight` | Right click |
| `MouseButtonMiddle` | Middle click |

### Mouse Wheel

```go
xoff, yoff := ebiten.Wheel()
if yoff > 0 {
    g.camera.ZoomIn()
}
if yoff < 0 {
    g.camera.ZoomOut()
}
```

Returns scroll offset. `yoff` is vertical scroll (positive = up), `xoff` is horizontal scroll.

---

## Gamepad

### Detecting Gamepads

```go
gamepadIDs := ebiten.AppendGamepadIDs(nil)
if len(gamepadIDs) == 0 {
    // no gamepad connected
}
```

### Standard Gamepad Layout

Ebitengine uses a standard gamepad abstraction that maps common controllers (Xbox, PlayStation, Switch) to uniform button/axis IDs:

| Button | Constant | Typical Mapping |
|--------|----------|-----------------|
| `StandardGamepadButtonRightBottom` | Face bottom (A/Cross) | |
| `StandardGamepadButtonRightRight` | Face right (B/Circle) | |
| `StandardGamepadButtonRightLeft` | Face left (X/Square) | |
| `StandardGamepadButtonRightTop` | Face top (Y/Triangle) | |
| `StandardGamepadButtonFrontTopLeft` | Left bumper (LB/L1) | |
| `StandardGamepadButtonFrontTopRight` | Right bumper (RB/R1) | |
| `StandardGamepadButtonFrontBottomLeft` | Left trigger (LT/L2) | |
| `StandardGamepadButtonFrontBottomRight` | Right trigger (RT/R2) | |
| `StandardGamepadButtonCenterLeft` | Select/Back | |
| `StandardGamepadButtonCenterRight` | Start | |
| `StandardGamepadButtonLeftStick` | Left stick press | |
| `StandardGamepadButtonRightStick` | Right stick press | |
| `StandardGamepadButtonDpadUp/Down/Left/Right` | D-pad directions | |

### Reading Buttons

```go
if ebiten.IsStandardGamepadButtonPressed(gamepadID, ebiten.StandardGamepadButtonRightBottom) {
    g.player.Jump()
}

if inpututil.IsStandardGamepadButtonJustPressed(gamepadID, ebiten.StandardGamepadButtonRightRight) {
    g.player.Dodge()
}
```

### Reading Axes (Analog Sticks)

```go
lx := ebiten.StandardGamepadAxisValue(gamepadID, ebiten.StandardGamepadAxisLeftStickHorizontal)
ly := ebiten.StandardGamepadAxisValue(gamepadID, ebiten.StandardGamepadAxisLeftStickHorizontal+1)
rx := ebiten.StandardGamepadAxisValue(gamepadID, ebiten.StandardGamepadAxisRightStickHorizontal)
ry := ebiten.StandardGamepadAxisValue(gamepadID, ebiten.StandardGamepadAxisRightStickHorizontal+1)
```

Axis values range from -1.0 to 1.0. Center is approximately 0.

### Deadzone

Always apply a deadzone to analog sticks to avoid drift:

```go
const deadzone = 0.25

func applyDeadzone(value float64) float64 {
    if value > -deadzone && value < deadzone {
        return 0
    }
    return value
}

lx := applyDeadzone(ebiten.StandardGamepadAxisValue(id, ebiten.StandardGamepadAxisLeftStickHorizontal))
ly := applyDeadzone(ebiten.StandardGamepadAxisValue(id, ebiten.StandardGamepadAxisLeftStickVertical))
```

### Trigger as Axis

```go
lt := ebiten.StandardGamepadAxisValue(id, ebiten.StandardGamepadAxisLeftStickHorizontal+4)
rt := ebiten.StandardGamepadAxisValue(id, ebiten.StandardGamepadAxisLeftStickHorizontal+5)
```

Trigger axes return 0.0 (released) to 1.0 (fully pressed).

---

## Touch

For mobile and touchscreen support:

```go
func (g *Game) Update() error {
    // Just pressed touches
    touchIDs := inpututil.AppendJustPressedTouchIDs(nil)
    for _, id := range touchIDs {
        x, y := ebiten.TouchPosition(id)
        g.handleTouchPress(x, y)
    }

    // Active touches
    activeIDs := inpututil.AppendPressedTouchIDs(nil)
    for _, id := range activeIDs {
        x, y := ebiten.TouchPosition(id)
        g.handleTouchDrag(x, y)
    }

    // Just released touches
    releasedIDs := inpututil.AppendJustReleasedTouchIDs(nil)
    for _, id := range releasedIDs {
        x, y := ebiten.TouchPosition(id)
        g.handleTouchRelease(x, y)
    }

    return nil
}
```

### Touch Functions

| Function | Purpose |
|----------|---------|
| `inpututil.AppendJustPressedTouchIDs(ids)` | IDs of touches that started this tick |
| `inpututil.AppendPressedTouchIDs(ids)` | IDs of currently active touches |
| `inpututil.AppendJustReleasedTouchIDs(ids)` | IDs of touches that ended this tick |
| `ebiten.TouchPosition(id)` | `(x, y)` position of specific touch |
| `inpututil.TouchPressDuration(id)` | How many ticks the touch has been held |

---

## Input Abstraction Pattern

Decouple physical inputs from game actions using an action mapper:

```go
type InputAction int

const (
    ActionMoveLeft InputAction = iota
    ActionMoveRight
    ActionMoveUp
    ActionMoveDown
    ActionJump
    ActionShoot
    ActionPause
    ActionMenuSelect
)

type InputMapper struct {
    keyBindings      map[InputAction][]ebiten.Key
    mouseBindings    map[InputAction][]ebiten.MouseButton
    gamepadBindings  map[InputAction][]ebiten.StandardGamepadButton
}

func NewInputMapper() *InputMapper {
    return &InputMapper{
        keyBindings: map[InputAction][]ebiten.Key{
            ActionMoveLeft:  {ebiten.KeyArrowLeft, ebiten.KeyA},
            ActionMoveRight: {ebiten.KeyArrowRight, ebiten.KeyD},
            ActionMoveUp:    {ebiten.KeyArrowUp, ebiten.KeyW},
            ActionMoveDown:  {ebiten.KeyArrowDown, ebiten.KeyS},
            ActionJump:      {ebiten.KeySpace},
            ActionShoot:     {ebiten.KeyJ},
            ActionPause:     {ebiten.KeyEscape, ebiten.KeyP},
            ActionMenuSelect: {ebiten.KeyEnter},
        },
        gamepadBindings: map[InputAction][]ebiten.StandardGamepadButton{
            ActionJump:       {ebiten.StandardGamepadButtonRightBottom},
            ActionShoot:      {ebiten.StandardGamepadButtonRightRight},
            ActionPause:      {ebiten.StandardGamepadButtonCenterRight},
            ActionMenuSelect: {ebiten.StandardGamepadButtonRightBottom},
        },
    }
}

func (m *InputMapper) IsActionPressed(action InputAction) bool {
    for _, key := range m.keyBindings[action] {
        if ebiten.IsKeyPressed(key) {
            return true
        }
    }
    for _, btn := range m.gamepadBindings[action] {
        for _, id := range ebiten.AppendGamepadIDs(nil) {
            if ebiten.IsStandardGamepadButtonPressed(id, btn) {
                return true
            }
        }
    }
    return false
}

func (m *InputMapper) IsActionJustPressed(action InputAction) bool {
    for _, key := range m.keyBindings[action] {
        if inpututil.IsKeyJustPressed(key) {
            return true
        }
    }
    for _, btn := range m.gamepadBindings[action] {
        for _, id := range ebiten.AppendGamepadIDs(nil) {
            if inpututil.IsStandardGamepadButtonJustPressed(id, btn) {
                return true
            }
        }
    }
    return false
}
```

### Using the Mapper

```go
func (g *Game) Update() error {
    if g.input.IsActionPressed(ActionMoveLeft) {
        g.player.X -= g.player.Speed
    }
    if g.input.IsActionJustPressed(ActionJump) {
        g.player.Jump()
    }
    return nil
}
```

---

## ebitengine-input Library

For a more complete Godot-inspired action input system:

```go
import "github.com/quasilyte/ebitengine-input"

type inputContext struct {
    inp *input.Input
}

func newInput() *inputContext {
    inp := input.New(input.SystemConfig{
        Keys: input.KeysConfig{
            MaxBindingsPerAction: 4,
        },
    })
    return &inputContext{inp: inp}
}
```

---

## Handling Multiple Input Sources

```go
func (g *Game) Update() error {
    // Check keyboard first, then gamepad, then touch
    if g.input.IsActionJustPressed(ActionJump) ||
        g.checkTouchJump() {
        g.player.Jump()
    }

    // Movement from any source
    dx, dy := g.getMovementVector()
    g.player.Move(dx, dy)

    return nil
}
```

---

## Input Recording (for replays)

```go
type InputEvent struct {
    Tick    int
    Actions []InputAction
}

type InputRecorder struct {
    events []InputEvent
    tick   int
}

func (r *InputRecorder) Record(mapper *InputMapper) {
    var actions []InputAction
    for action := ActionMoveLeft; action <= ActionMenuSelect; action++ {
        if mapper.IsActionPressed(action) {
            actions = append(actions, action)
        }
    }
    if len(actions) > 0 {
        r.events = append(r.events, InputEvent{Tick: r.tick, Actions: actions})
    }
    r.tick++
}
```

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Use `IsKeyPressed()` for single actions | Use `inpututil.IsKeyJustPressed()` for one-shot events |
| Poll gamepad without checking connection | Check `AppendGamepadIDs()` first |
| Skip deadzone on analog sticks | Apply a 0.15-0.25 deadzone always |
| Hard-code key bindings | Use an input mapper / action system |
| Handle only keyboard | Support gamepad and touch where possible |
| Read `CursorPosition()` in `Draw()` | Read input only in `Update()` |
| Mix input reading with game logic | Separate input polling from action handling |
| Ignore touch input for mobile targets | Use touch IDs for multi-touch support |
| Create new slices in hot path for `AppendPressedKeys` | Reuse slice: `keys = inpututil.AppendPressedKeys(keys[:0])` |

## When to Use
This skill is applicable when implementing or modifying input handling in an Ebitengine game: keyboard, mouse, gamepad, or touch.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
