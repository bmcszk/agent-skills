---
name: shell-startup-files
description: Use when editing zsh or bash startup files, placing env vars, or debugging why a shell session, cron job, or ssh command missed its environment - sourcing matrix, guards, and per-host branching.
license: MIT
metadata:
  audience: sysadmins
  workflow: maintenance
  category: os-administration
  technologies: bash, zsh, systemd, environment.d
---

# Shell startup files

## The sourcing matrix

- zsh non-interactive reads `.zshenv` ONLY.
- bash non-interactive reads NOTHING.
- A non-login ssh bash command reads `.bashrc`: env loading goes
  ABOVE the interactivity guard or `ssh host command` runs without
  the environment.

## environment.d confs are parsed literally

systemd `environment.d` confs are parsed literally while shell
eval-loops expand: no variable expansion and no command substitution
inside a conf, or the two consumers silently diverge on the same
variable. One wrong conf feeds a shell `$HOME` and a systemd unit
the literal string `$HOME`.

## Daemons spawned from rc files

An rc-spawned daemon dies with the shell unless it gets its own
session: launch with `setsid`. A new `env.d` conf is invisible to
the running user manager until `systemctl import-environment` (or a
daemon-restart) picks it up.

## The interactivity guard

`zsh -i` with no controlling tty still sets `-o interactive`, so an
`[[ -o interactive ]]` guard alone is not a tty check: test
`-t 0` AND `-t 1`, and make the guard the first executable line -
anything above it runs in every non-interactive consumer too.

## Per-host branching

Branch per host on runtime guards, never on parsed files: `$HOSTNAME`
in bash, `$HOST` in zsh. The lowercase `$hostname` exists in neither
by default and is silently empty, so a lowercase branch matches every
host at once.

## Test battery for rc edits

Before shipping a startup-file change, run: `bash -n` and `zsh -n`
(syntax), `env -i bash` (cron simulation), `bash -lc 'echo $PATH'`
(login PATH reset check), and `zsh -ic 'alias'` asserts (interactive
aliases present).
