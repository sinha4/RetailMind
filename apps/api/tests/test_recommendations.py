from fastapi.testclient import TestClient

from retailmind_api.main import app
from retailmind_api.recommendations import extract_intent

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
    assert len(payload["trace"]) == 5

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
