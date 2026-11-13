# Glossary format

## Structure

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## Rules

- Be opinionated: when multiple words exist for the same concept, pick
  the best one and list the others under `_Avoid_`.
- Keep definitions tight: one or two sentences max, what the term IS,
  not what it does.
- Project-specific terms only: general programming concepts (timeouts,
  error types, utility patterns) stay out even when the project uses
  them extensively.
- Group terms under subheadings when natural clusters emerge; a flat
  list is fine when all terms belong to one cohesive area.

## Single vs multi-context repos

A single-context repo (most repos) keeps one `GLOSSARY.md` at the
repo root. Multiple contexts get a `GLOSSARY-MAP.md` at the root
listing the contexts, where they live, and how they relate:

```md
# Glossary Map

## Contexts

- [Ordering](./src/ordering/GLOSSARY.md): receives and tracks customer orders
- [Billing](./src/billing/GLOSSARY.md): generates invoices and processes payments
- [Fulfillment](./src/fulfillment/GLOSSARY.md): manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

Which structure applies: a `GLOSSARY-MAP.md` means read it to find
the contexts; a lone root `GLOSSARY.md` means single context; neither
means create the root glossary lazily when the first term resolves.

When multiple contexts exist, infer which one the current topic relates to. If unclear, ask.
