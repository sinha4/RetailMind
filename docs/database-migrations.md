# Qdrant schema migrations

RetailMind uses forward-only, idempotent Qdrant migrations instead of relying on implicit seeding.
The migration ledger is stored as a reserved schema point in the same collection, which makes the
current version portable across embedded, Docker, and hosted Qdrant deployments.

## Current schema

| Version | Migration                          | Effect                                                                                |
| ------- | ---------------------------------- | ------------------------------------------------------------------------------------- |
| 1       | `add_memory_query_indexes`         | Adds keyword indexes for customer, attribute, sentiment, source, and product filters. |
| 2       | `backfill_payload_schema_metadata` | Tags existing facts with `recordType=memory_fact` and `schemaVersion=2`.              |

Every newly written fact includes the current schema version. Fact IDs are deterministic UUIDs, so
retries remain idempotent. Migrations run automatically before seed data is checked.

## Manual operation

With the API environment configured, run:

```bash
PYTHONPATH=apps/api/src .venv/bin/python scripts/migrate-memory.py
```

Back up hosted Qdrant before adding a destructive migration. New migrations must use the next
integer version, preserve existing payload meaning, include an in-memory Qdrant test, and document
their rollback or recovery strategy. The current migrations are additive; recovery is restoring the
pre-migration snapshot if required.
