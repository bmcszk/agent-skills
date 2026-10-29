### Write-back comments (audit verdicts, review notes)

There is NO `beans comment` subcommand. Attach a dated note to a bean with
the CLI:

```bash
beans update <id> --body-append "## AUDIT (reviewer, date, scope): verdict + evidence"
```
