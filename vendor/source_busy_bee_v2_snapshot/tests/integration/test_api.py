from fastapi.testclient import TestClient

from busy_bee.api.app import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_finance_governance_blocks_without_approval() -> None:
    client = TestClient(create_app())
    response = client.post("/governance/finance/execute")
    assert response.status_code == 403
