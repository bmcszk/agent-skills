---
name: android-debloat
description: De-bloat, speed up, and maintain Android phones over adb — no root. Use when the user says their phone is slow or laggy, wants bloatware removed or disabled, asks to free phone storage or move media to a memory card, reports battery drain, or asks for adb-based Android maintenance, diagnostics, or rollback of phone changes. Covers diagnosis (RAM/swap, wakeup floods, disk fullness), safe package disabling, verified bulk file moves, and rollback discipline.
license: MIT
metadata:
  category: device-maintenance
  technologies: adb, android
---

# Android debloat & speed over adb (no root)

Works on any Android 9+ phone with USB debugging. Verify on the actual device every time — vendor behavior differs (Sony, Samsung, Xiaomi remove features silently).

## Diagnose before touching anything

Run all four; each maps to a distinct root cause:

```bash
adb devices -l                                        # must say "device", not "unauthorized"
adb shell df -h /storage/emulated | tail -1           # >90% full → Android itself degrades
adb shell top -b -n 1 | head -8                       # kswapd0 high CPU = RAM starvation (THE hidden killer)
adb shell dumpsys meminfo | grep -E "Free RAM|ZRAM"   # big ZRAM/swapped = swap tax on every app switch
adb shell dumpsys alarm | grep -B1 -A3 wakeups        # who wakes the CPU (battery + lag)
```

Leading insight: **kswapd burning CPU means RAM starvation, not CPU weakness**. Fix = uninstall big unused apps + reboot (clears swap). No amount of "cleaner" apps helps.

## Safe-action ladder (most reversible first)

1. `adb shell pm trim-caches 512G` — purge all app caches instantly
2. `adb shell pm disable-user --user 0 <pkg>` — reversible bloat kill (`pm enable <pkg>` reverts). Prefer over uninstall.
3. `adb shell pm uninstall --user 0 <pkg>` — user apps the user names explicitly (Play Store reinstallable)
4. `adb shell settings put global window_animation_scale 0.5` (+ `transition_animation_scale`, `animator_duration_scale`) — visible snappiness, `1.0` reverts
5. NEVER `pm uninstall` system-critical pkgs (SystemUI, phone, providers). If UAD says Unsafe/Expert, skip.

## Debloat database

Pull [UAD-ng lists](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation): `raw.githubusercontent.com/.../main/resources/assets/uad_lists.json` (5k+ pkgs, `removal: Recommended/Advanced/Expert/Unsafe`). Cross-reference with `adb shell pm list packages -s`, then **apply user-context overrides**: keep aptX/BT codecs if BT headphones, keep SIM/uim on modem-dependent devices, keep anything the user's apps depend on. `Recommended` ≠ always safe for THIS user.

Log every change to a file on the phone (`/data/local/tmp/debloat.log`) — it is the rollback ledger.

## Bulk file moves to microSD (the slow path that works)

microSD over adb is ~2–4 MB/s (FUSE + exFAT). Never block an interactive session:

1. Push a shell script to `/data/local/tmp/`, run detached: `adb shell 'nohup sh script.sh >/dev/null 2>&1 &'`
2. Script does per-item: `cp -a` → compare file count AND byte totals → delete source only on exact match → append verdict to a log
3. Poll the log from the host. No reboot while it runs (kills the job).
4. MTP won't show adb-copied files in `Music/DCIM/Pictures` (different uid) — files are fine; check with an on-device file manager.

Hard limits (verify per device, don't assume): WhatsApp media and app cannot move to SD (hardcoded + vendor killed adoptable storage on Android 9+). Google Maps offline areas CAN move: in-app → Offline maps → ⚙ → Storage preferences → SD card (requires re-download).

## Known traps

- Phone toybox `sort` lacks `-h` → use `du -k` + `sort -rn`
- `dumpsys diskstats` size arrays are positional — never map indexes to package names (mis-blames apps); use `du -k -d 1 /storage/emulated/0/Android/media` and `Android/data` instead
- `pm clear` frees ~0 when the bloat lives in `Android/media` (shared storage), not app-private `/data/data`
- `ps -A | grep cp` may miss busybox cp; use `pidof cp`
- Syncthing `.stfolder` markers = active sync — check sync direction before deleting on either side
- Vendor telemetry (Sony devicemonitor/crashmonitor, FB services) can fire 1k–7k alarms/day; disabling them is the cheapest battery+CPU win

## Per-phone state

Device-specific ledgers (what was changed, rollback list, storage map) live in per-project docs — e.g. `scripts/sony-xperia-xq-es54/README.md` on this machine. Check for a similar dir before re-diagnosing a phone already worked on.
