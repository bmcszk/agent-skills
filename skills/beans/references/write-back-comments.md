### Write-back comments (audit verdicts, review notes)

There is NO `beans comment` subcommand. Attach a dated note to a bean with
the CLI:

```bash
beans update <id> --body-append "## AUDIT (brainer 2026-10-24, scope): verdict + evidence"
```

A `## LABEL (context)` heading form keeps repo-level beans-lint section
checks (triage evidence, PoW detection) working. Never hand-edit
`.beans/*.md` to add comments - the CLI owns the file format and etag.

On create, pass the title as the POSITIONAL argument
(`beans create "Title" -t task ...`): creating with only `-d`/`--body-file`
leaves the filename slug at `untitled`, and a later `update --title` fixes
the displayed title WITHOUT renaming the file - the id slug is permanent.

A repo may add its own `beans-lint` script that checks more than the CLI
(dossier rules: required sections, skill paths with full `SKILL.md`
suffixes, triage-evidence citations). Run it after EVERY bean mutation - it fails serially (one rule per run), so loop `beans-lint` → fix → re-run
until clean before committing. Skill paths in a bean body must include
the `/SKILL.md` suffix to count, and triage sections must contain the
lint's expected keyword (e.g. "brainer") to register as evidence - wording that reads fine to a human fails the check.