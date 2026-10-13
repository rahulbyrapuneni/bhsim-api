from fastapi.testclient import TestClient
from main import app

# ---TEST CLIENT---
client = TestClient(app)

# ---TEST HEALTH ENDPOINT---
def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ---TEST INVALID DATASET REQUEST---
def test_invalid_clients():
    response = client.post(
        "/v1/datasets",
        json={
            "clients": -10,
            "employees": 20,
            "history_months": 12,
            "seed": 42
        }
    )

    assert response.status_code == 422


# ---TEST DATASET GENERATION---
def test_dataset_generation():
    response = client.post(
        "/v1/datasets",
        json={
            "clients": 10,
            "employees": 5,
            "history_months": 1,
            "seed": 42
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "completed"
    assert data["validation"]["valid"] is True
    assert data["validation"]["issues"] == []
    assert "dataset_id" in data