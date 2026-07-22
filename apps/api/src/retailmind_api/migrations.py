"""Forward-only Qdrant schema migrations for customer memory."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from uuid import NAMESPACE_URL, uuid5

SCHEMA_VERSION = 2
MIGRATION_POINT_ID = str(uuid5(NAMESPACE_URL, "retailmind:qdrant-schema"))


@dataclass(frozen=True)
class QdrantMigration:
    version: int
    name: str
    apply: Callable[[Any, Any, str], None]


def _add_query_indexes(client: Any, models: Any, collection: str) -> None:
    """Index fields used in memory filters and operational investigations."""
    for field in ("customerId", "attribute", "sentiment", "source", "productId"):
        client.create_payload_index(
            collection_name=collection,
            field_name=field,
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )


def _backfill_payload_metadata(client: Any, models: Any, collection: str) -> None:
    """Tag pre-migration facts so future payload changes remain inspectable."""
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=collection,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        fact_ids = [
            point.id for point in points if point.payload and point.payload.get("customerId")
        ]
        if fact_ids:
            client.set_payload(
                collection_name=collection,
                payload={"recordType": "memory_fact", "schemaVersion": 2},
                points=fact_ids,
                wait=True,
            )
        if offset is None:
            break


MIGRATIONS = (
    QdrantMigration(1, "add_memory_query_indexes", _add_query_indexes),
    QdrantMigration(2, "backfill_payload_schema_metadata", _backfill_payload_metadata),
)


class QdrantMigrationRunner:
    """Apply each migration once and persist the current version in Qdrant."""

    def __init__(self, client: Any, models: Any, collection: str) -> None:
        self._client = client
        self._models = models
        self._collection = collection

    def current_version(self) -> int:
        records = self._client.retrieve(
            collection_name=self._collection,
            ids=[MIGRATION_POINT_ID],
            with_payload=True,
            with_vectors=False,
        )
        if not records or not records[0].payload:
            return 0
        return int(records[0].payload.get("schemaVersion", 0))

    def run(self) -> int:
        current = self.current_version()
        for migration in MIGRATIONS:
            if migration.version <= current:
                continue
            migration.apply(self._client, self._models, self._collection)
            self._write_version(migration)
            current = migration.version
        return current

    def _write_version(self, migration: QdrantMigration) -> None:
        self._client.upsert(
            collection_name=self._collection,
            points=[
                self._models.PointStruct(
                    id=MIGRATION_POINT_ID,
                    vector=[0.0],
                    payload={
                        "recordType": "schema_migration",
                        "schemaVersion": migration.version,
                        "migrationName": migration.name,
                    },
                )
            ],
            wait=True,
        )
