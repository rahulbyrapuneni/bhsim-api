from fastapi.testclient import TestClient
from main import app
from uuid import uuid4

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

# ---TEST DATASET RETRIEVAL---
def test_dataset_retrieval():
    create_response = client.post(
        "/v1/datasets",
        json={
            "clients": 10,
            "employees": 5,
            "history_months": 1,
            "seed": 42
        }
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    response = client.get(f"/v1/datasets/{dataset_id}")

    assert response.status_code == 200
    assert response.json()["dataset_id"] == dataset_id
    assert response.json()["file_size_bytes"] > 0


# ---TEST DATASET DOWNLOAD---
def test_dataset_download():
    create_response = client.post(
        "/v1/datasets",
        json={
            "clients": 10,
            "employees": 5,
            "history_months": 1,
            "seed": 42
        }
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    response = client.get(
        f"/v1/datasets/{dataset_id}/download"
    )

    assert response.status_code == 200

    # ---VERIFY SQLITE FILE HEADER---
    assert response.content.startswith(b"SQLite format 3")


# ---TEST MISSING DATASET---
def test_missing_dataset():
    missing_id = str(uuid4())

    response = client.get(f"/v1/datasets/{missing_id}")

    assert response.status_code == 404


# ---TEST INVALID DATASET ID---
def test_invalid_dataset_id():
    response = client.get("/v1/datasets/not-a-valid-uuid")

    assert response.status_code == 422