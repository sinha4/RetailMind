from fastapi.testclient import TestClient

from retailmind_api.main import app

client = TestClient(app)


def test_catalog_contains_seed_products() -> None:
    response = client.get("/v1/products")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 30
    assert len(payload["products"]) == 30
    assert payload["products"][0]["currency"] == "INR"
    assert payload["products"][0]["totalStock"] > 0


def test_catalog_filters_by_customer_constraints() -> None:
    response = client.get(
        "/v1/products",
        params={"material": "linen", "occasion": "beach", "maxPrice": 5000, "size": "M"},
    )

    assert response.status_code == 200
    products = response.json()["products"]
    assert products
    assert all("linen" in [item.lower() for item in product["materials"]] for product in products)
    assert all(product["price"] <= 5000 for product in products)


def test_catalog_returns_one_product() -> None:
    response = client.get("/v1/products/rm-dress-001")

    assert response.status_code == 200
    assert response.json()["name"] == "Azure Linen Midi Dress"


def test_catalog_returns_404_for_unknown_product() -> None:
    response = client.get("/v1/products/not-a-product")

    assert response.status_code == 404
