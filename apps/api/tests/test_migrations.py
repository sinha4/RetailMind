from qdrant_client import QdrantClient, models

from retailmind_api.migrations import MIGRATION_POINT_ID, SCHEMA_VERSION, QdrantMigrationRunner


def test_qdrant_migrations_are_versioned_backfilled_and_idempotent() -> None:
    client = QdrantClient(location=":memory:")
    collection = "migration-test"
    client.create_collection(
        collection_name=collection,
        vectors_config=models.VectorParams(size=1, distance=models.Distance.COSINE),
    )
    client.upsert(
        collection_name=collection,
        points=[
            models.PointStruct(
                id=1,
                vector=[1.0],
                payload={"customerId": "demo-customer", "attribute": "color", "value": "blue"},
            )
        ],
    )

    runner = QdrantMigrationRunner(client, models, collection)
    assert runner.current_version() == 0
    assert runner.run() == SCHEMA_VERSION

    migrated = client.retrieve(collection_name=collection, ids=[1], with_payload=True)[0]
    assert migrated.payload["recordType"] == "memory_fact"
    assert migrated.payload["schemaVersion"] == SCHEMA_VERSION

    marker = client.retrieve(
        collection_name=collection, ids=[MIGRATION_POINT_ID], with_payload=True
    )[0]
    assert marker.payload["schemaVersion"] == SCHEMA_VERSION
    assert marker.payload["migrationName"] == "backfill_payload_schema_metadata"

    assert runner.run() == SCHEMA_VERSION
    assert len(client.retrieve(collection_name=collection, ids=[MIGRATION_POINT_ID])) == 1
