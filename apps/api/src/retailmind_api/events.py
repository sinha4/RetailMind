from datetime import UTC, datetime
from functools import lru_cache
from uuid import uuid4

from retailmind_api.agents import retention_message
from retailmind_api.catalog import get_catalog
from retailmind_api.memory import CustomerNotFoundError, get_memory_repository, get_seed_contexts
from retailmind_api.models import (
    AgentTraceStep,
    CustomerSignal,
    CustomerSignalRequest,
    MemoryFact,
    Product,
    SignalIngestionResponse,
)


class ProductNotFoundError(LookupError):
    pass


@lru_cache
def get_event_store() -> dict[str, list[CustomerSignal]]:
    return {}


def list_customer_events(customer_id: str) -> list[CustomerSignal]:
    if customer_id not in get_seed_contexts():
        raise CustomerNotFoundError(customer_id)
    return list(get_event_store().get(customer_id, []))


def reset_customer_events(customer_id: str) -> None:
    if customer_id not in get_seed_contexts():
        raise CustomerNotFoundError(customer_id)
    get_event_store().pop(customer_id, None)


def _product_fact(
    signal: CustomerSignal, sentiment: str, confidence: float, evidence: str
) -> MemoryFact:
    return MemoryFact(
        id=f"memory-{signal.id}-product",
        customerId=signal.customer_id,
        attribute="product",
        value=signal.product_id,
        sentiment=sentiment,
        confidence=confidence,
        source="return" if signal.kind == "return" else "event",
        occurredAt=signal.occurred_at,
        evidence=evidence,
        productId=signal.product_id,
    )


def _derive_memories(signal: CustomerSignal, product: Product) -> list[MemoryFact]:
    if signal.kind == "wishlist":
        return [_product_fact(signal, "positive", 0.7, f"Saved {product.name} to the wishlist.")]
    if signal.kind == "purchase":
        return [_product_fact(signal, "positive", 0.9, f"Purchased {product.name}.")]
    if signal.kind == "skip":
        return [_product_fact(signal, "negative", 0.45, f"Skipped {product.name}.")]
    if signal.kind == "return":
        reason = signal.reason or "No return reason was provided."
        facts = [_product_fact(signal, "negative", 0.98, f"Returned {product.name}: {reason}")]
        if signal.reason and any(
            term in signal.reason.casefold() for term in ("fabric", "material", "itch", "hot")
        ):
            facts.extend(
                MemoryFact(
                    id=f"memory-{signal.id}-material-{index}",
                    customerId=signal.customer_id,
                    attribute="material",
                    value=material,
                    sentiment="negative",
                    confidence=0.92,
                    source="return",
                    occurredAt=signal.occurred_at,
                    evidence=f"Returned {product.name}: {reason}",
                    productId=product.id,
                )
                for index, material in enumerate(product.materials)
            )
        return facts
    return []


def ingest_signal(request: CustomerSignalRequest) -> SignalIngestionResponse:
    if request.customer_id not in get_seed_contexts():
        raise CustomerNotFoundError(request.customer_id)

    product = next((item for item in get_catalog() if item.id == request.product_id), None)
    if product is None:
        raise ProductNotFoundError(request.product_id)

    signal = CustomerSignal(
        id=str(uuid4()),
        customerId=request.customer_id,
        productId=request.product_id,
        kind=request.kind,
        occurredAt=datetime.now(UTC),
        reason=request.reason,
    )
    get_event_store().setdefault(request.customer_id, []).append(signal)

    memories = _derive_memories(signal, product)
    repository = get_memory_repository()
    for memory in memories:
        repository.upsert_fact(memory)

    agent_message = (
        retention_message(request.customer_id, product.name) if signal.kind == "purchase" else None
    )
    trace = (
        [
            AgentTraceStep(
                agent="post-purchase",
                summary="Acknowledged the purchase and prepared retention context.",
                mode="deterministic",
            )
        ]
        if signal.kind == "purchase"
        else []
    )
    return SignalIngestionResponse(
        signal=signal, derivedMemories=memories, agentMessage=agent_message, trace=trace
    )
