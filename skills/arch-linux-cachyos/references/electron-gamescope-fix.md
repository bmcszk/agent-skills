# Electron apps in gamescope-session — full fix

**Three independent failures can cause "black screen + Steam spinner" when launching Discord, Heroic, or any Electron app from Steam in a gamescope-session. Fix ALL or only one will appear to work.**

## Failure A: Electron picks Wayland instead of XWayland

gamescope is a Wayland compositor but does **not** expose its Wayland socket by default (would need `--expose-wayland`). `gamescope-session-cachyos` only sets `--xwayland-count`, never `--expose-wayland`. Electron 27+ auto-picks Ozone-Wayland when `XDG_SESSION_TYPE=wayland` OR `WAYLAND_DISPLAY` is set; both leak into the env from `dbus-update-activation-environment` in `start-gamescope-session`. Electron connects to a Wayland display gamescope isn't serving → silent failure, no window.

**Fix**: per-app wrapper script forcing `--ozone-platform=x11` so Electron uses gamescope's XWayland server (`--xwayland-count=N`).

## Failure B: Steam shortcut's LaunchOptions is not the wrapper

The wrapper script alone does **not** change what Steam launches. Steam shortcuts store the absolute Exe path in `~/.steam/steam/userdata/<id>/config/shortcuts.vdf`. Setting `LaunchOptions="--ozone-platform=x11"` on the raw binary path does **not** survive Steam's launch-wrapper environment filtering in all cases — Steam may still launch the raw binary without the wrapper's full env.

**Fix**: rewrite the shortcut's `Exe` field to point at the wrapper script itself (and clear `LaunchOptions`).

## Failure C: shortcut is force-pinned to proton-cachyos-slr

Steam pins specific non-Steam shortcuts to `proton-cachyos-slr` via `CompatToolMapping` in `~/.steam/steam/config/config.vdf`, keyed by appid. Linux-native ELFs (Heroic = `2385805048`) routed through proton **cannot** run — proton expects a Windows PE, sees an ELF, exits in ~4 s. Steam shows "Preparing launch" indefinitely, user sees black screen + spinner.

**Fix**: remove the bad `CompatToolMapping` entry (regex matches only entries pinned to `proton-cachyos-slr`; benign refs to the same appid like `ShaderCacheSize`/`SizeOnDisk` elsewhere in the file are untouched).

## Failure D: Steam overlay LD_PRELOAD crashes Electron 42 zygote

Steam injects its overlay into every launched shortcut via `LD_PRELOAD=...gameoverlayrenderer.so` (32- and 64-bit paths). On Electron 42+ (Discord 1.0.157; Heroic 2.22/Electron 41 borderline) the overlay **crashes the zygote host at init**:

```
FATAL:content/browser/zygote_host/zygote_host_impl_linux.cc:207] Check failed: . : Invalid argument (22)
```

Process dies in ~1 s, no window, Steam spinner forever. `DISPLAY=:0` vs `:1` (gamescope's two XWayland servers) is **irrelevant** — verified matrix: both displays fine without the overlay; `:1` + overlay preload = instant FATAL even with `--disable-gpu` / `--disable-gpu-sandbox`.

**Fix**: the wrapper must strip `gameoverlayrenderer.so` from `LD_PRELOAD` before exec and set `ENABLE_VK_LAYER_VALVE_steam_overlay_1=0`. Loss of the Steam overlay in a chat app / launcher is harmless.

**Testing rule**: manually running the wrapper from a terminal NEVER reproduces this — your shell lacks Steam's injected `LD_PRELOAD`, so a fix that "works when tested" can still die when launched from Steam. Verify with the exact Steam env:

```bash
env -i HOME=$HOME USER=$USER LOGNAME=$USER PATH=/usr/bin:/bin \
  XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
  DISPLAY=:1 \
  LD_PRELOAD=":$HOME/.local/share/Steam/ubuntu12_32/gameoverlayrenderer.so:$HOME/.local/share/Steam/ubuntu12_64/gameoverlayrenderer.so" \
  ENABLE_VK_LAYER_VALVE_steam_overlay_1=1 \
  /home/blaze/scripts/discord-gamescope.sh & sleep 15
pgrep -f 'Discord --ozone' && echo PASS   # PID present + no FATAL in wrapper output
```

## Procedure

`/home/blaze/scripts/fix-electron-gamescope.sh` does all three fixes idempotently. After it runs, the only remaining step is restarting Steam so it re-reads the two config files:

```bash
# Close any running game first — this terminates gamescope + Steam + your session
systemctl --user restart gamescope-session.target
```

The script does **not** restart Steam automatically; that would interrupt in-progress work.

## What the script produces

| App | Wrapper | .desktop | Repointed shortcut | CompatToolMapping |
|---|---|---|---|---|
| Discord | `/home/blaze/scripts/discord-gamescope.sh` | `~/.local/share/applications/discord-gamescope.desktop` | yes | not pinned (was already absent) |
| Heroic | `/home/blaze/scripts/heroic-gamescope.sh` | `~/.local/share/applications/heroic-gamescope.desktop` | yes | entry removed (was `proton-cachyos-slr`) |

Add more apps to the `APPS=(...)` array at the top of the script + extend the in-script `if 'name' in name or 'name' in exe` dispatch in the Python block.

## Wrapper content (template)

```bash
#!/bin/bash
# Strip Steam overlay preload (gameoverlayrenderer.so crashes Electron 42+ zygote)
if [ -n "${LD_PRELOAD:-}" ]; then
    NEW_LP=""
    IFS=':' read -ra _parts <<< "$LD_PRELOAD"
    for _p in "${_parts[@]}"; do
        case "$_p" in
            *gameoverlayrenderer.so*) ;;
            "") ;;
            *) NEW_LP="${NEW_LP:+$NEW_LP:}$_p" ;;
        esac
    done
    export LD_PRELOAD="$NEW_LP"
fi
export ENABLE_VK_LAYER_VALVE_steam_overlay_1=0
exec "/path/to/real/binary" --ozone-platform=x11 "$@"
```

`--ozone-platform=x11` is the only universal knob. `ELECTRON_OZONE_PLATFORM_HINT` was removed in Electron 38 (`https://github.com/electron/electron/issues/48001`); Heroic 2.22 bundles Electron 41. Arch's `discord` package does **not** read `~/.config/electron-flags.conf`, so the standard "electron flags" mechanism does not work — the wrapper is mandatory.

## Restarting from terminal (not the gamescope-session console)

`systemctl --user restart gamescope-session.target` works from any terminal session where `DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus` and `XDG_RUNTIME_DIR=/run/user/1000` are set (the standard user env on CachyOS). plasmalogin-autologin auto-respawns the session — you do not need to be physically at tty1, no manual re-login. New gamescope and Steam PIDs appear within a few seconds.

**DO NOT** try `pkill -9 -f 'gamescope|steam'` from a non-root terminal: `plasmalogin-helper` is owned by root (`Operation not permitted`), and SIGKILL-ing yourself while killing other PIDs can take out your own shell with no recovery.

## Verification (after restart)

```bash
# Confirm shortcuts were repointed (Exe should be the wrapper path, LaunchOptions empty)
python3 -c "import vdf; d=vdf.binary_load(open('/home/blaze/.steam/steam/userdata/<id>/config/shortcuts.vdf','rb')); [print(s.get('AppName'),'->',s.get('Exe'),'LaunchOpts=',s.get('LaunchOptions','')) for s in d.get('shortcuts',{}).values()]"

# Confirm Heroic removed from CompatToolMapping (regex precise; only the proton-cachyos-slr block)
grep -c '"2385805048"' /home/blaze/.steam/steam/config/config.vdf  # 2 is OK (ShaderCacheSize + SizeOnDisk)
grep -B1 -A4 'CompatToolMapping' /home/blaze/.steam/steam/config/config.vdf | grep '2385805048'  # should be empty

# Test wrapper with gamescope env (XWayland requires DISPLAY)
DISPLAY=:0 /home/blaze/scripts/heroic-gamescope.sh --version  # should print nile sync, then hang waiting for UI; Ctrl-C
```

## Pitfall: shortcuts.vdf edit must use python-vdf, not byte patching

Steam's `shortcuts.vdf` is binary VDF (Steam's own format, not KeyValues text). Replacing `"/opt/Heroic/heroic"` with a wrapper path of different length by sed/python byte-slice **breaks offsets** and Steam fails to parse the whole file (all shortcuts disappear). Use `vdf.binary_load` + `vdf.binary_dump`. Install: `pip install vdf --break-system-packages`.

## Pitfall: Steam `userdata/` placeholder `0/`

`/home/blaze/.steam/steam/userdata/0/` is a placeholder Steam creates on first launch; it has no real user state. Iterating `userdata/*/config` naively picks it first. Filter to `dirname >= 1` AND require `shortcuts.vdf` to exist before patching.

## Pitfall: `grep -q '"$appid"'` is too broad in config.vdf

The same appid appears in `ShaderCacheSize`, `SizeOnDisk`, and `CompatToolMapping` blocks. Use a precise regex matching the `proton-cachyos-slr` block shape, not a substring grep, or you'll repeatedly "fix" the same entry.

## Pitfall: never put debug `env | sort`-style capture INSIDE a Steam-launched wrapper

The overlay preload hooks every spawned process, including `env`/`sort` helpers a debug block spawns; the wrapper then deadlocks in `__futex_wait` on ValveIPC shared memory and Steam spins forever — the debug instrumentation itself becomes the failure. If Steam's env is needed, capture it once as the wrapper's FIRST action (`env > /tmp/file` before anything else spawns), or replay a previously captured env file instead.

## Pitfall: Discord self-updates on first launch after a long gap

Discord's updater (log: `~/.config/discord/logs/*updater*rCURRENT.log`) can download a new version (e.g. 1.0.152 -> 1.0.157) during launch; the old process is killed mid-flight and the window never appears even with a correct wrapper. Before deep-diving, check that log for a fresh `Requesting manifest` entry and just relaunch once.

## Rollback

`/home/blaze/scripts/rollback-electron-gamescope.sh` removes wrappers + .desktop files. The shortcuts.vdf and config.vdf edits are **not** rolled back — restore from the timestamped `*.bak-<epoch>` files created next to each patched file:

```bash
ls -lt ~/.steam/steam/userdata/*/config/shortcuts.vdf.bak-* | head -1
# cp <newest backup> ~/.steam/steam/userdata/<id>/config/shortcuts.vdf
```

Then restart Steam.
