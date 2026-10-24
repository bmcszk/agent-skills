## Reopen pattern (user finding contradicts completed bean)

When a user identifies a gap in a bean whose PoW claimed clean:
1. Append a `REOPENED` section to the bean's body (CLI `beans update -s
   in-progress --body-append "..."`) citing the exact findings and the
   research file.
2. Create a successor bean (new ID) with the fix scope; do NOT silently
   re-close the original - the audit trail must show the reopen.
3. In the reopened bean's body, note the successor ID and its status.
4. Only after the successor completes and passes parent All-x-All
   re-verification may the original bean be considered resolved.