# Window/state API reference

Load when configuring window mode, FPS mode, or reading runtime FPS/TPS.

## Window Configuration

| Function | Purpose |
|----------|---------|
| `SetWindowSize(w, h int)` | Window size in device-independent pixels |
| `SetWindowTitle(title string)` | Window title |
| `SetWindowResizingMode(mode)` | `WindowResizingModeDisabled`, `WindowResizingModeOnlyFullscreenEnabled`, `WindowResizingModeEnabled` |
| `SetWindowDecorated(decorated bool)` | Show/hide title bar |
| `SetWindowPosition(x, y int)` | Window position |
| `SetWindowFloating(float bool)` | Keep window on top |
| `SetWindowMousePassthrough(on bool)` | Click-through window |
| `SetFullscreen(fullscreen bool)` | Toggle fullscreen |
| `SetFPSMode(mode)` | `FPSModeVsyncOn` (default), `FPSModeVsyncOffMaximum`, `FPSModeVsyncOffMinimum` |
| `SetTPS(tps int)` | Ticks per second (default 60) |
| `SetScreenClearedEveryFrame(cleared bool)` | Auto-clear screen before Draw |
| `SetScreenFilterEnabled(enabled bool)` | Enable/disable screen scaling filter |
| `SetVsyncEnabled(enabled bool)` | VSync control |

### Read State

| Function | Returns |
|----------|---------|
| `WindowSize()` | `(w, h int)` |
| `IsFullscreen()` | `bool` |
| `IsWindowDecorated()` | `bool` |
| `WindowPosition()` | `(x, y int)` |
| `CurrentFPS()` | `float64` |
| `CurrentTPS()` | `float64` |
| `ActualFPS()` | `float64` |
| `ActualTPS()` | `float64` |
| `IsFocused()` | `bool` |
| `IsScreenTransparent()` | `bool` |

---

