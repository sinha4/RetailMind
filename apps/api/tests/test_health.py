from fastapi.testclient import TestClient

from retailmind_api.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health", headers={"x-request-id": "test-request"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "retailmind-api"}
    assert response.headers["x-request-id"] == "test-request"


def test_readiness_checks_catalog_and_memory() -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "catalog": "30 products",
        "memory": "5 facts",
    }


def test_prometheus_metrics_are_exposed() -> None:
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "retailmind_http_requests_total" in response.text
    assert "retailmind_http_latency_ms" in response.text
