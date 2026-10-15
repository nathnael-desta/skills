# Speeding up database-backed test suites

Reach for these in order; re-measure with `--durations` after each.

1. **Build the schema once per session.** Create tables and extensions in one session-scoped fixture. A suite that creates and drops every schema per test pays that DDL hundreds of times.
2. **Isolate each test with a transaction.** Open one connection and an outer transaction per test, bind the session to it with SQLAlchemy 2.0's `join_transaction_mode="create_savepoint"`, and roll back at teardown. A `commit()` inside the test then releases a savepoint and is undone. The `get_db`/client override must hand out a session bound to that same connection.
3. **Mark the tests that must really commit** (DDL, `TRUNCATE`, background tasks on their own connection, assertions on commit boundaries, `SET LOCAL`). They run against a fixture that truncates the tables afterwards instead of rolling back.
4. **Add `pytest-xdist` with one database per worker**, named from `PYTEST_XDIST_WORKER`. Each worker repeats the session-scoped schema build, and each worker's pool needs room under the server's `max_connections`.
5. **Template databases** (`CREATE DATABASE ... TEMPLATE`) suit tests that must commit: about 33 ms per clone in one measurement. The template must have zero other sessions, so one template per worker.
6. **Durability flags** (`fsync=off`, tmpfs) gave 0 to 16% across the reports found, and slightly slower under xdist in one. Try last, alone, so its effect is measurable.

## Pitfalls

- A session-scoped async engine under pytest-asyncio needs `loop_scope="session"` on the fixture and a matching test loop scope, or asyncpg raises "attached to a different loop".
- Code that opens its own engine or connection cannot see uncommitted test rows; it belongs in the commit-marker tier.
- Measured in one repo: 810 s to 113 s for a unit suite on 2 cores, from steps 1 to 4 plus caching one expensive parsed file.

Sources: SQLAlchemy 2.0 docs, "Joining a Session into an External Transaction"; SQLAlchemy discussion 13109; a Litestar/SQLAlchemy xdist benchmark (habr.com/ru/articles/1047134).
