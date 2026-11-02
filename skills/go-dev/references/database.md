# Go database access

Derived from samber/cc-skills-golang (MIT): golang-database/SKILL.md, golang-database/references/{scanning,transactions,performance}.md.

Use this when writing, reviewing, or debugging Go code that talks to PostgreSQL, MySQL, MariaDB, or SQLite: queries, scanning, transactions, pooling, migrations.

Library choice is not decided here. It follows [go-setup](../../go-setup/references/libraries.md) and the repo's existing pattern; once chosen, this ref covers usage. Match the repo's driver: samples show both `sqlx` and `pgx` variants, and the repo's one wins.

Before adding a query, grep the repo for its existing query and naming patterns. Repo consistency outranks a generic recipe.

Version gate: never use a stdlib API newer than the `go` directive in `go.mod`.

## Hard rules

- Parameterized placeholders only. Never concatenate input into SQL.
- Pass context to every operation: `QueryContext`, `ExecContext`, `GetContext`.
- Handle `sql.ErrNoRows` explicitly with `errors.Is`, to separate "not found" from a real error.
- `defer rows.Close()` right after `QueryContext`, and check `rows.Err()` after the loop.
- Use `Exec` for statements that return no rows. `Query` returns `*Rows` that must be closed, or the connection leaks.
- Wrap multi-statement writes in a transaction.
- Use `SELECT ... FOR UPDATE` when you read a value, compute from it, and write it back.
- Raise the isolation level when the default is not enough.
- Model NULLable columns with pointer fields or `sql.NullXxx`.
- Configure the pool: `SetMaxOpenConns`, `SetMaxIdleConns`, `SetConnMaxLifetime`, `SetConnMaxIdleTime`.
- Migrations use an external tool with human-reviewed SQL: `golang-migrate` is the repo default; Flyway and Atlas are the alternatives.
- Batch in reasonable sizes, not row by row and not millions at once.
- Do not create or modify schemas. Index and DDL changes are suggestions for a human.
- Do not rely on triggers, views, materialized views, stored procedures, or row-level security.

## Parameterized queries

Placeholders per driver: `$1` for PostgreSQL, `?` for MySQL and SQLite.

- Dynamic `IN` clauses build a placeholder list and pass the values as arguments.
- Column names and `ORDER BY` fields are never interpolated from input. Map the input through an allowlist to a fixed identifier.

## Scanning

- `sqlx`: `db:"column_name"` tags, `StructScan`, `GetContext`.
- `pgx` v5: `pgx.CollectRows` with `pgx.RowToStructByName`.
- A struct that serves JSON too keeps both tag sets. A pointer field encodes as `null` when the column is NULL.

## NULLable columns

Three approaches, best first:

1. Pointer fields (`*string`, `*time.Time`). Clean, and JSON marshaling works without custom code.
2. `sql.NullXxx`, or the generic `sql.Null[T]` (Go 1.22). Explicit but verbose, and needs custom JSON marshaling.
3. `COALESCE` in the query, which moves the decision into SQL.

## Errors

| Error | Detect with | Action |
|---|---|---|
| Row not found | `errors.Is(err, sql.ErrNoRows)` | Return a domain error |
| Unique constraint | Driver-specific error code | Return a conflict error |
| Connection refused | `db.PingContext` error | Fail fast, log, retry with backoff |
| Serialization failure | PostgreSQL code `40001` | Retry the whole transaction |
| Context canceled | `errors.Is(err, context.Canceled)` | Stop and propagate |

Error text and wrapping rules live in [error-handling.md](error-handling.md).

## Transactions

```go
tx, err := db.BeginTx(ctx, nil)
if err != nil {
	return fmt.Errorf("begin: %w", err)
}
defer tx.Rollback() // no-op after a successful Commit
```

- Commit explicitly, and return the commit error. The deferred rollback is a safety net, not the happy path.
- Isolation levels:

| Level | Use when |
|---|---|
| `LevelReadCommitted` | Default, fine for most work |
| `LevelRepeatableRead` | Reads inside the transaction must be consistent |
| `LevelSerializable` | Money, inventory, strict consistency |

- Locking clauses:

| Clause | Effect |
|---|---|
| `FOR UPDATE` | Locks rows for write; others block on the same rows |
| `FOR UPDATE NOWAIT` | Same, but fails immediately instead of waiting |
| `FOR SHARE` | Locks rows against writes, allows other reads |

## Connection pool

| Setting | Too low | Too high |
|---|---|---|
| `MaxOpenConns` | Requests queue for a connection | Database overwhelmed, context switches |
| `MaxIdleConns` | Cold connections, slow queries | Memory held for idle connections |
| `ConnMaxLifetime` | Reconnection overhead | Stale connections after a failover |
| `ConnMaxIdleTime` | Same as `MaxIdleConns` too low | Idle connections hold server memory |

Read `db.Stats()` in production. A climbing `WaitCount` means either raise `MaxOpenConns` or fix the slow queries. The `go_sql_*` metrics (from `database/sql` stats, via a Prometheus collector the service already runs) are the ones to watch: `go_sql_open_connections`, `go_sql_in_use_connections`, `go_sql_wait_count_total`, `go_sql_wait_duration_seconds_total`. Dashboard and alert wiring is deployment configuration, not skill content. Pool sizing interacts with caching and batching; see [performance.md](performance.md).

## Batch and pagination

- Sweet spot is 100 to 1,000 rows per batch. Larger rows, smaller batches.
- PostgreSQL bulk insert uses `pgx.CopyFrom` (binary COPY), which beats a multi-row `INSERT`.
- For large result sets, move the cursor instead of `OFFSET`. `OFFSET` re-scans skipped rows and degrades as the page number grows. Pick the cursor column from a real index (`created_at`, `id`).

## Indexes

Never create or drop an index. Present findings with data and let the owner decide.

Suggest adding:

- Foreign key columns (PostgreSQL does not index them automatically).
- Columns used in `WHERE`, `JOIN`, `ORDER BY`.
- A composite index for multi-column queries, leftmost column most selective.
- A partial index for a filtered query.

Suggest removing:

- Indexes with near-zero scans.
- Duplicates over the same columns in the same order.
- Narrower replacement for a wide composite index.
- Indexes on write-heavy tables that cost more than they save.

## Query tips

- `EXPLAIN ANALYZE` before optimizing. Measure, do not guess.
- List columns explicitly. `SELECT *` fetches what you do not use and breaks scanning on a schema change.
- `LIMIT` always comes with `ORDER BY`.
- `EXISTS` beats `COUNT` for an existence check.
- Remove N+1 queries with a `JOIN` or a batched `WHERE id IN (...)`.

## Schema work

This ref stops at schema creation. An AI-written schema is often subtly wrong: missing index, wrong type, bad normalization, missing constraint. Schema design needs data volumes, access patterns, and production constraints that a reviewer has and a model does not. Use dedicated tooling and human review.

## Testing database code

Database behaviour is integration test territory, owned by [go-tests](../../go-tests/SKILL.md): Docker Compose, real database, directory-based levels. No mocks, no `sqlmock`, no testcontainers default, no build tags.
