## Bean creation for code-fix tasks (ALL-CODE-DELEGATED)

- Use `beans create -t task -s todo --parent <epic> --tag audit-gap
   -p high --body-file <contract.md> "Title"` with the full contract
   text in the body file (not inline - avoids escaping issues).
- Contract must include: research reference, exact acceptance criteria
   as checkboxes, required skills (full `SKILL.md` paths), and the
   RE-SHUFFLE law reference (coding-rules intro).
- Commit `.beans/` and push; hooks must stay green - never bypass
  them.

---