# Git config reference

Reference config for a machine that obeys the git SKILL.md laws: pulls
never rewrite, branches push without ceremony, recorded conflict
resolutions replay. Every block runs on a real machine; adapt names,
emails, and paths.

## Global config (~/.gitconfig)

```ini
[user]
	name = <real name>
	email = <real email>

[core]
	editor = nvim

[push]
	autoSetupRemote = true

[merge "ours"]
	driver = true

[pull]
	ff = only

[fetch]
	prune = true

[diff]
	algorithm = histogram

[rerere]
	enabled = true
	autoUpdate = false

[gpg "ssh"]
	allowedSignersFile = ~/.ssh/allowed_signers
```

Per-key behavior:

- `push.autoSetupRemote`: git 2.37+. First push of a new branch sets its
  upstream; no `--set-upstream`.
- `pull.ff = only`: a diverged pull refuses loudly instead of merging or
  rewriting. This is the merge-over-rebase law in config. Audit for
  rebase-on-pull overrides before trusting a clone:

  ```bash
  git config --show-origin --get-regexp '^(pull\.rebase|branch\.[^.]+\.rebase)'
  ```

- `fetch.prune`: deleted remote branches drop on every fetch.
- `diff.algorithm = histogram`: cleaner hunks around moved code.
- `rerere`: replays recorded conflict resolutions. `autoUpdate` stays
  false so the replay lands unstaged and gets reviewed before continue.
- `merge "ours"` driver: inert until a `.gitattributes` names it (below).
- `gpg.ssh.allowedSignersFile`: lets `git log --show-signature` verify
  SSH-signed commits; one line per identity: `<email> <keytype> <key>`.

## Per-host includes

Keep global config identity-free; hosts override identity, signing, and
url rewriting through conditional includes. The `hasconfig` conditions
match clones by remote URL wherever they live (git 2.36+):

```ini
[includeIf "gitdir:~/github/<org>/"]
	path = ~/github/<org>/.gitconfig
[includeIf "hasconfig:remote.*.url:git@github.com:<org>/**"]
	path = ~/github/<org>/.gitconfig
[includeIf "hasconfig:remote.*.url:https://github.com/<org>/**"]
	path = ~/github/<org>/.gitconfig
```

`~/github/<org>/.gitconfig` (per-host file, lives outside any repo):

```ini
[gpg]
	format = ssh
[user]
	signingkey = "ssh-ed25519 AAAA...<public key material>"
	name = <name for this host>
	email = <email for this host>
[commit]
	gpgsign = true
[core]
	excludesFile = ~/github/<org>/.gitignore
[url "git@github.com:<org>"]
	insteadOf = https://github.com/<org>
```

Laws:

- `gpg.format = ssh` needs git 2.34+; `signingkey` carries the PUBLIC key
  (the same key registered with the forge shows commits as Verified).
- `excludesFile` holds per-host untracked noise (agent dot-dirs and
  friends); it complements, never replaces, the repo-level `.gitignore`.
- `url.insteadOf` makes https clones push over ssh.
- A second host (gitlab) duplicates the same file shape with its own
  `gitdir:` and `insteadOf` blocks.
- `hasconfig`-included files must not declare remote urls; git forbids it
  to break the resolution cycle.
- Older git silently IGNORES unknown includeIf conditions; verify a
  condition resolves in the repo you expect:

  ```bash
  git config --show-origin --list | grep -F '<org>/.gitconfig'
  ```

## merge=ours attributes

`[merge "ours"] driver = true` activates only through `.gitattributes`.
Paths marked `merge=ours` keep the current branch's version wholesale on
conflict; non-conflicting incoming changes still merge in.

```
# .gitattributes
generated.lock merge=ours
```

Reserve it for regenerable files, and read the merged result afterwards:
the incoming side of a conflict is discarded without a visible diff.

## Verify a fresh machine

```bash
git config --global --list --show-origin
git var GIT_COMMITTER_IDENT
git log --show-signature -1    # on a repo with signed history
```
