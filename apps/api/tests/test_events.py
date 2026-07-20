from fastapi.testclient import TestClient

from retailmind_api.events import get_event_store
from retailmind_api.main import app
from retailmind_api.memory import get_memory_repository

client = TestClient(app)


def test_wishlist_event_is_recorded_and_becomes_memory() -> None:
    try:
        response = client.post(
            "/v1/events",
            json={
                "customerId": "demo-customer",
                "productId": "rm-top-001",
                "kind": "wishlist",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["signal"]["kind"] == "wishlist"
        assert payload["derivedMemories"][0]["sentiment"] == "positive"

        events_response = client.get("/v1/customers/demo-customer/events")
        assert events_response.status_code == 200
        assert events_response.json()[0]["productId"] == "rm-top-001"
    finally:
        get_event_store.cache_clear()
        get_memory_repository.cache_clear()


def test_return_reason_creates_strong_product_and_material_memories() -> None:
    try:
        response = client.post(
            "/v1/events",
            json={
                "customerId": "demo-customer",
                "productId": "rm-top-002",
                "kind": "return",
                "reason": "The fabric felt too hot.",
            },
        )

        assert response.status_code == 200
        memories = response.json()["derivedMemories"]
        assert any(fact["attribute"] == "product" for fact in memories)
        assert any(fact["attribute"] == "material" for fact in memories)
        assert all(fact["sentiment"] == "negative" for fact in memories)
    finally:
        get_event_store.cache_clear()
        get_memory_repository.cache_clear()


def test_event_rejects_unknown_product() -> None:
    response = client.post(
        "/v1/events",
        json={
            "customerId": "demo-customer",
            "productId": "missing-product",
            "kind": "skip",
        },
    )

    assert response.status_code == 404
