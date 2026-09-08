---
name: arch-linux-triage
description: 'Triage and resolve Arch Linux issues with pacman, systemd, and rolling-release best practices.'
---

# Arch Linux Triage

You are an Arch Linux expert. Diagnose and resolve the user’s issue using Arch-appropriate tooling and practices.

## Inputs

- `${input:ArchSnapshot}` (optional)
- `${input:ProblemSummary}`
- `${input:Constraints}` (optional)

## Instructions

1. Confirm recent updates and environment assumptions.
2. Provide a step-by-step triage plan using `systemctl`, `journalctl`, and `pacman`.
3. Offer remediation steps with copy-paste-ready commands.
4. Include verification commands after each major change.
5. Address kernel update or reboot considerations where relevant.
6. Provide rollback or cleanup steps.

## Output Format

- **Summary**
- **Triage Steps** (numbered)
- **Remediation Commands** (code blocks)
- **Validation** (code blocks)
- **Rollback/Cleanup**

## Reference notes (verified on this box)

### Electron app silently fails to open in gamescope-session

**Symptom:** App (Discord, Heroic, Obsidian, VSCode, …) works in KDE/Wayland but
shows no window when launched inside `gamescope-session.desktop` (Steam Big
Picture mode, SteamOS mode). No crash dialog, no log. Window never appears.

**Root cause (verified):** gamescope is a Wayland compositor but does **not**
expose its Wayland socket by default. ArchWiki "Gamescope#Wayland support":
> "Gamescope does not support Wayland clients by default. To enable support
> for Wayland clients, add the `--expose-wayland` flag."

`gamescope-session-cachyos` only sets `--xwayland-count 2`, never
`--expose-wayland`. Electron 27+ auto-selects Ozone-Wayland when
`XDG_SESSION_TYPE=wayland` OR `WAYLAND_DISPLAY` is set. Both can leak into the
env: `start-gamescope-session` runs
`dbus-update-activation-environment --systemd DESKTOP_SESSION \`env | grep ^XDG_\``
which syncs XDG_* (including `XDG_SESSION_TYPE=wayland` from the parent shell
or SDDM) into the systemd user env before the service overrides it for its own
process. Electron then tries Wayland, fails to find a display, exits silently.

**Fix:** exec the binary with `--ozone-platform=x11` (Chromium flag, works on
all Electron 27+). The `ELECTRON_OZONE_PLATFORM_HINT` env var was removed in
Electron 38 (https://github.com/electron/electron/issues/48001), so the CLI
flag is the only universal knob. Arch's `discord` package does NOT read
`~/.config/electron-flags.conf`, so a wrapper is the only reliable mechanism.

**Canonical fix:** `fix-electron-gamescope.sh` in `/home/blaze/scripts/`. Idempotent.
Handles Discord (Electron 37) + Heroic (Electron 41) + any other Electron app
by adding to the `APPS=()` list at the top.
