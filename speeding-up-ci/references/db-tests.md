# Speeding up database-backed test suites

Reach for these in order; re-measure with `--durations` after each, and compare the pass/skip set before and after (a faster suite that skips more is not faster).

Result in one project (a FastAPI and SQLAlchemy async backend, 17 Postgres schemas, about 400 database tests): unit suite 810 s to 113 s on a 2-core runner, identical pass/skip set, from steps 1 to 4 plus caching one expensive parsed file.

## 1. Build the schema once per session

Create extensions and tables in one session-scoped fixture. A suite that runs `create_all` and `DROP SCHEMA ... CASCADE` per test pays hundreds of DDL statements per test. Find it first: a large `setup` time per test in `--durations` output.

## 2. Isolate each test with an outer transaction

Open one connection and begin an outer transaction per test, bind the session to that connection with `join_transaction_mode="create_savepoint"`, and roll back at teardown. A `commit()` inside the test releases a savepoint and is undone with the outer transaction.

```python
@pytest_asyncio.fixture
async def db_session(engine):
    async with engine.connect() as conn:
        outer = await conn.begin()
        session = AsyncSession(bind=conn, join_transaction_mode="create_savepoint",
                               expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await outer.rollback()
```

- The HTTP client fixture's dependency override (`get_db` or equivalent) must hand out a session bound to the **same connection**, or its writes escape the rollback.
- Anything that opens its own engine or connection (background tasks, queue-dispatch code, a raw `asyncpg.connect`) cannot see uncommitted test rows. Those tests belong to step 3.
- Per-test cost drops from DDL to `BEGIN`, `SAVEPOINT`, `ROLLBACK`: milliseconds. No independent timing for this swap on async SQLAlchemy was found; measure it.

## 3. Mark the tests that must really commit

DDL, `TRUNCATE`, code on its own connection, assertions on commit or rollback boundaries, `SET LOCAL`. Give them a marker (for example `@pytest.mark.commits`) and a fixture that uses the real engine, then `TRUNCATE ... CASCADE` the touched tables afterwards instead of rolling back. Keep the tier small: it is the slow one.

## 4. `pytest-xdist` with one database per worker

```python
@pytest.fixture(scope="session")
def database_url(worker_id):          # provided by xdist; "master" without it
    name = f"test_{worker_id}" if worker_id != "master" else "test"
    ...                               # CREATE DATABASE <name> if absent, return its URL
```

- Each worker repeats the session-scoped schema build; each worker's pool needs room under the server's `max_connections` (pool size plus overflow, times workers).
- Isolation failures show up here first: shared files, module-level state, fixed ports, tests that rely on order. Fix them, do not fall back to `-n0`.
- Expected gain on a 2-vCPU runner is about 1.6x at best because Postgres shares the cores. One independent benchmark on 14 cores: 94 s serial, 57 s at `-n2`, 38 s at `-n4`, 28 s at `-n14`.

## 5. Cache an expensive parse

If tests reload and re-parse a large file (a document, a fixture dataset, a schema), cache the result keyed on a hash of the file's **text**, in a module-level or session-scoped cache. Keying on mtime or path serves stale data after an edit.

## 6. Template databases, for the commit tier

`CREATE DATABASE ... TEMPLATE` clones a prepared schema: about 33 ms per clone in one benchmark, against about 9 ms for per-test `DELETE`. The template must have zero other sessions, and a stranded connection on it wedges every clone; use one template per xdist worker and `NullPool` for the connection that holds it.

## 7. Durability flags, last and alone

`fsync=off`, `full_page_writes=off`, tmpfs data directory gave 0 to 16% across the reports found, and slightly slower under xdist in one. Try it after everything else so its effect is measurable. On GitHub Actions a service container cannot take a `command`: name the service in `options`, run `psql -c "ALTER SYSTEM SET ..."`, `docker restart` it, and wait for readiness.

## Pitfalls

- A session-scoped async engine under pytest-asyncio needs `loop_scope="session"` on the fixture and a matching loop scope for the tests (`asyncio_default_test_loop_scope = "session"` or `@pytest.mark.asyncio(loop_scope="session")`), or asyncpg raises "attached to a different loop". Check the installed pytest-asyncio version's docs; this changed across 0.23 to 1.x.
- If the existing engine was function-scoped with `NullPool`, nobody has hit the loop-scope problem yet. You will when widening it.
- The SQLAlchemy 2.0 docs recipe for joining a session into an external transaction is sync; the async form is the same mechanism on `AsyncConnection`.

Sources: SQLAlchemy 2.0 docs, "Joining a Session into an External Transaction or Savepoint"; SQLAlchemy discussion 13109; a Litestar and SQLAlchemy xdist benchmark (habr.com/ru/articles/1047134); GitLab MR 27295 for durability flags.
