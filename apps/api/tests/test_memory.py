from fastapi.testclient import TestClient

from retailmind_api.main import app

client = TestClient(app)


def test_demo_customer_context_contains_profile_and_attributable_memory() -> None:
    response = client.get("/v1/customers/demo-customer/context")

    assert response.status_code == 200
    context = response.json()
    assert context["profile"]["displayName"] == "Maya"
    assert context["profile"]["sizes"]["dress"] == "M"
    assert len(context["memories"]) == 5

    polyester_fact = next(
        fact for fact in context["memories"] if fact["value"] == "polyester"
    )
    assert polyester_fact["sentiment"] == "negative"
    assert polyester_fact["source"] == "return"
    assert polyester_fact["confidence"] == 0.98
    assert polyester_fact["evidence"]


def test_unknown_customer_returns_404() -> None:
    response = client.get("/v1/customers/unknown/context")

    assert response.status_code == 404
