import json
from functools import lru_cache
from pathlib import Path
from typing import Protocol
from uuid import NAMESPACE_URL, uuid5

from retailmind_api.config import Settings, get_settings
from retailmind_api.models import CustomerContext, CustomerProfile, MemoryFact

CUSTOMERS_PATH = Path(__file__).parent / "data" / "customers.json"


class CustomerNotFoundError(LookupError):
    pass


class MemoryRepository(Protocol):
    def list_facts(self, customer_id: str) -> list[MemoryFact]: ...

    def upsert_fact(self, fact: MemoryFact) -> None: ...

    def reset_customer(self, customer_id: str) -> list[MemoryFact]: ...


@lru_cache
def get_seed_contexts() -> dict[str, CustomerContext]:
    with CUSTOMERS_PATH.open(encoding="utf-8") as customer_file:
        records = json.load(customer_file)

    contexts = [CustomerContext.model_validate(record) for record in records]
    return {context.profile.customer_id: context for context in contexts}


class SeededMemoryRepository:
    def __init__(self) -> None:
        self._facts = {
            customer_id: list(context.memories)
            for customer_id, context in get_seed_contexts().items()
        }

    def list_facts(self, customer_id: str) -> list[MemoryFact]:
        return list(self._facts.get(customer_id, []))

    def upsert_fact(self, fact: MemoryFact) -> None:
        facts = self._facts.setdefault(fact.customer_id, [])
        facts[:] = [existing for existing in facts if existing.id != fact.id]
        facts.append(fact)

    def reset_customer(self, customer_id: str) -> list[MemoryFact]:
        context = get_seed_contexts().get(customer_id)
        if context is None:
            raise CustomerNotFoundError(customer_id)
        self._facts[customer_id] = list(context.memories)
        return self.list_facts(customer_id)


class QdrantMemoryRepository:
    """Qdrant payload store for attributable facts; semantic vectors come later."""

    def __init__(self, settings: Settings) -> None:
        try:
            from qdrant_client import QdrantClient, models
        except ImportError as error:
            raise RuntimeError(
                "Qdrant memory requires the API agents extra: pip install -e 'apps/api[agents]'"
            ) from error

        self._models = models
        self._collection = settings.qdrant_collection
        if settings.qdrant_url.startswith("local:"):
            local_path = settings.qdrant_url.removeprefix("local:") or "qdrant_storage"
            self._client = QdrantClient(path=local_path)
        else:
            self._client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
            )
        if not self._client.collection_exists(self._collection):
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=models.VectorParams(size=1, distance=models.Distance.COSINE),
            )
        self._seed_if_empty()

    def _seed_if_empty(self) -> None:
        for context in get_seed_contexts().values():
            if not self.list_facts(context.profile.customer_id):
                for fact in context.memories:
                    self.upsert_fact(fact)

    def list_facts(self, customer_id: str) -> list[MemoryFact]:
        points, _ = self._client.scroll(
            collection_name=self._collection,
            scroll_filter=self._models.Filter(
                must=[
                    self._models.FieldCondition(
                        key="customerId", match=self._models.MatchValue(value=customer_id)
                    )
                ]
            ),
            limit=100,
            with_payload=True,
            with_vectors=False,
        )
        return [MemoryFact.model_validate(point.payload) for point in points]

    def upsert_fact(self, fact: MemoryFact) -> None:
        self._client.upsert(
            collection_name=self._collection,
            points=[
                self._models.PointStruct(
                    id=str(uuid5(NAMESPACE_URL, fact.id)),
                    vector=[1.0],
                    payload=fact.model_dump(mode="json", by_alias=True),
                )
            ],
        )

    def reset_customer(self, customer_id: str) -> list[MemoryFact]:
        context = get_seed_contexts().get(customer_id)
        if context is None:
            raise CustomerNotFoundError(customer_id)
        self._client.delete(
            collection_name=self._collection,
            points_selector=self._models.FilterSelector(
                filter=self._models.Filter(
                    must=[
                        self._models.FieldCondition(
                            key="customerId",
                            match=self._models.MatchValue(value=customer_id),
                        )
                    ]
                )
            ),
            wait=True,
        )
        for fact in context.memories:
            self.upsert_fact(fact)
        return self.list_facts(customer_id)


@lru_cache
def get_memory_repository() -> MemoryRepository:
    settings = get_settings()
    if settings.memory_backend.casefold() == "qdrant":
        return QdrantMemoryRepository(settings)
    return SeededMemoryRepository()


def get_customer_context(customer_id: str) -> CustomerContext:
    seeded_context = get_seed_contexts().get(customer_id)
    if seeded_context is None:
        raise CustomerNotFoundError(customer_id)

    return CustomerContext(
        profile=seeded_context.profile,
        memories=get_memory_repository().list_facts(customer_id),
    )


def get_customer_profile(customer_id: str) -> CustomerProfile:
    context = get_seed_contexts().get(customer_id)
    if context is None:
        raise CustomerNotFoundError(customer_id)
    return context.profile


def reset_customer_memory(customer_id: str) -> list[MemoryFact]:
    """Restore one demo customer's memory to the versioned seed facts."""
    return get_memory_repository().reset_customer(customer_id)
