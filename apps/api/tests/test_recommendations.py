import asyncio
import json

from fastapi.testclient import TestClient

from retailmind_api.ai import ModelOutput
from retailmind_api.config import Settings
from retailmind_api.main import app
from retailmind_api.models import ConversationMessageRequest
from retailmind_api.recommendations import extract_intent, handle_shopping_turn

client = TestClient(app)


def test_extracts_structured_shopping_intent() -> None:
    intent = extract_intent("I need a blue linen dress for the beach under ₹5,000 in size M")

    assert intent.occasion == "beach"
    assert intent.categories == ["dress"]
    assert intent.materials == ["linen"]
    assert intent.colors == ["blue"]
    assert intent.max_price == 5000
    assert intent.size == "M"


def test_conversation_returns_grounded_personalized_recommendations() -> None:
    response = client.post(
        "/v1/conversations/messages",
        json={
            "customerId": "demo-customer",
            "message": "Find me a beach holiday outfit under ₹5,000",
            "brandVoice": "warm",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"]["occasion"] == "beach"
    assert len(payload["recommendations"]) == 3
    assert len(payload["trace"]) == 6
    assert payload["escalation"]["required"] is False

    for recommendation in payload["recommendations"]:
        product = recommendation["product"]
        assert product["price"] <= 5000
        assert product["totalStock"] > 0
        assert all("polyester" not in material.lower() for material in product["materials"])
        assert recommendation["reason"]["evidence"]


def test_explicit_constraints_are_respected() -> None:
    response = client.post(
        "/v1/conversations/messages",
        json={
            "customerId": "demo-customer",
            "message": "I want a blue linen dress for the beach under 5000 in size M",
        },
    )

    assert response.status_code == 200
    recommendations = response.json()["recommendations"]
    assert recommendations
    assert all(item["product"]["category"] == "dress" for item in recommendations)
    assert all("linen" in item["product"]["materials"] for item in recommendations)


def test_unknown_customer_returns_404_for_conversation() -> None:
    response = client.post(
        "/v1/conversations/messages",
        json={"customerId": "unknown", "message": "Find me a beach outfit"},
    )

    assert response.status_code == 404


class FakeGeminiAdapter:
    async def generate(self, prompt: str, *, response_schema: dict | None = None) -> ModelOutput:
        text = (
            json.dumps(
                {
                    "occasion": "beach",
                    "categories": [],
                    "materials": ["linen", "cotton"],
                    "colors": ["blue"],
                    "maxPrice": 6000,
                    "size": None,
                }
            )
            if response_schema
            else "Maya, your considered holiday edit is ready."
        )
        return ModelOutput(text=text, latency_ms=42, provider="fake-gemini", model="test")


class FailingGeminiAdapter:
    async def generate(self, prompt: str, *, response_schema: dict | None = None) -> ModelOutput:
        raise TimeoutError("provider unavailable")


class IntentProviderAdapter:
    async def generate(self, prompt: str, *, response_schema: dict | None = None) -> ModelOutput:
        assert response_schema is not None
        return ModelOutput(
            text=json.dumps(
                {
                    "occasion": "beach",
                    "categories": ["dress"],
                    "materials": ["linen"],
                    "colors": ["blue"],
                    "maxPrice": 5000,
                    "size": "M",
                }
            ),
            latency_ms=12,
            provider="google-gemini",
            model="gemini-test",
        )


class BrandProviderAdapter:
    async def generate(self, prompt: str, *, response_schema: dict | None = None) -> ModelOutput:
        assert response_schema is None
        return ModelOutput(
            text="Maya, your considered coastal edit is ready.",
            latency_ms=18,
            provider="lyzr-agent",
            model="lyzr-test-agent",
        )


def test_ai_intent_and_brand_output_are_validated_and_traced() -> None:
    response = asyncio.run(
        handle_shopping_turn(
            ConversationMessageRequest(
                customerId="demo-customer",
                message="Something breezy for Goa, preferably blue, under 6k",
            ),
            adapter=FakeGeminiAdapter(),
        )
    )

    assert response.intent.occasion == "beach"
    assert response.intent.max_price == 6000
    assert response.assistant_message == "Maya, your considered holiday edit is ready."
    assert response.trace[0].mode == "ai"
    assert response.trace[0].provider == "fake-gemini"
    assert response.trace[0].latency_ms == 42
    assert response.trace[-2].mode == "ai"


def test_ai_failure_is_visible_and_uses_deterministic_fallback() -> None:
    response = asyncio.run(
        handle_shopping_turn(
            ConversationMessageRequest(
                customerId="demo-customer",
                message="A blue linen beach dress under 5000",
            ),
            adapter=FailingGeminiAdapter(),
        )
    )

    assert response.recommendations
    assert response.trace[0].provider == "fallback"
    assert "TimeoutError" in response.trace[0].summary
    assert response.trace[-2].provider == "fallback"


def test_orchestrator_uses_gemini_for_intent_and_lyzr_for_brand(monkeypatch) -> None:
    import retailmind_api.recommendations as orchestration

    monkeypatch.setattr(
        orchestration,
        "get_settings",
        lambda: Settings(
            gemini_api_key="gemini-test-key",
            lyzr_api_key="lyzr-test-key",
            lyzr_agent_id="lyzr-test-agent",
        ),
    )
    monkeypatch.setattr(orchestration, "GeminiAdapter", lambda settings: IntentProviderAdapter())
    monkeypatch.setattr(orchestration, "LyzrAdapter", lambda settings: BrandProviderAdapter())

    response = asyncio.run(
        handle_shopping_turn(
            ConversationMessageRequest(
                customerId="demo-customer",
                message="Find a blue linen beach dress under 5000 in size M",
            )
        )
    )

    assert response.trace[0].provider == "google-gemini"
    assert response.trace[-2].provider == "lyzr-agent"
    assert response.assistant_message == "Maya, your considered coastal edit is ready."


def test_demo_reset_restores_seed_memory_and_clears_events() -> None:
    client.post(
        "/v1/events",
        json={
            "customerId": "demo-customer",
            "productId": "rm-dress-001",
            "kind": "wishlist",
        },
    )

    response = client.post("/v1/demo/reset?customerId=demo-customer")

    assert response.status_code == 200
    assert response.json()["memoryCount"] == 5
    assert client.get("/v1/customers/demo-customer/events").json() == []


def test_purchase_runs_post_purchase_agent() -> None:
    response = client.post(
        "/v1/events",
        json={
            "customerId": "demo-customer",
            "productId": "rm-dress-001",
            "kind": "purchase",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "Great choice" in payload["agentMessage"]
    assert payload["trace"][0]["agent"] == "post-purchase"


def test_long_delivery_delay_escalates_to_human() -> None:
    response = client.post(
        "/v1/orders/delivery-delay",
        json={
            "customerId": "demo-customer",
            "orderId": "RM-1001",
            "productId": "rm-dress-001",
            "delayDays": 8,
            "brandVoice": "warm",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["escalation"]["required"] is True
    assert payload["trace"][0]["agent"] == "post-purchase"
    assert payload["trace"][1]["agent"] == "human-escalation"


def test_brand_manager_profiles_are_available() -> None:
    response = client.get("/v1/brands")

    assert response.status_code == 200
    assert {profile["id"] for profile in response.json()} == {"warm", "minimal", "bold"}
