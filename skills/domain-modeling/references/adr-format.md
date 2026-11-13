# ADR format

ADRs live in `docs/adr/` (created lazily, on the first record) with
sequential numbering: `0001-slug.md`, `0002-slug.md`.

## Template

```md
# {Short title of the decision}

{1-3 sentences: context, the decision, and why.}
```

An ADR can be a single paragraph. The value is in recording that a
decision was made and why, not in filling out sections.

## Optional sections

Only when they add genuine value; most records need none:

- **Status** frontmatter (`proposed | accepted | deprecated |
  superseded by ADR-NNNN`) for decisions that get revisited.
- **Considered Options** only when the rejected alternatives are
  worth remembering.
- **Consequences** only when non-obvious downstream effects need
  calling out.

## What qualifies for a record

- Architectural shape ("the write model is event-sourced, the read
  model is projected").
- Integration patterns between contexts ("domain events, not
  synchronous HTTP").
- Technology choices that carry lock-in: database, message bus, auth
  provider, deployment target. The ones that would take a quarter to
  swap, not every library.
- Boundary and scope decisions, where the explicit no-s matter as
  much as the yes-s ("Customer data is owned by the Customer context;
  others reference it by ID only").
- Deliberate deviations from the obvious path, which stop the next
  engineer from "fixing" something deliberate.
- Constraints not visible in the code ("response times under 200ms
  because of the partner API contract").
- Rejected alternatives when the rejection is non-obvious.
