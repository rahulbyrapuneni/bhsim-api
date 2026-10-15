
import pytest
from uuid import uuid4
from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app
import main

# ---TEST CONFIGURATION---
TEST_API_KEY = "bhsim-test-key-only"

client = TestClient(app)

AUTH_HEADERS = {
    "X-API-Key": TEST_API_KEY
}

VALID_PAYLOAD = {
    "clients": 10,
    "employees": 5,
    "history_months": 1,
    "seed": 42
}


# ---CONFIGURE TEST ENVIRONMENT---
@pytest.fixture(autouse=True)
def configure_test_environment(monkeypatch):
    monkeypatch.setenv("BHSIM_API_KEY", TEST_API_KEY)

    # ---MOCK DAILY QUOTA---
    monkeypatch.setattr(
        main,
        "consume_daily_quota",
        lambda api_key: 1
    )

    # ---MOCK REQUEST LOGGING---
    monkeypatch.setattr(
        main,
        "log_api_request",
        lambda **kwargs: None
    )


# ---TEST HEALTH ENDPOINT---
def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ---TEST INVALID DATASET REQUEST---
def test_invalid_clients():
    response = client.post(
        "/v1/datasets",
        json={**VALID_PAYLOAD, "clients": -10},
        headers=AUTH_HEADERS
    )

    assert response.status_code == 422


# ---TEST DATASET GENERATION---
def test_dataset_generation():
    response = client.post(
        "/v1/datasets",
        json=VALID_PAYLOAD,
        headers=AUTH_HEADERS
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
        json=VALID_PAYLOAD,
        headers=AUTH_HEADERS
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    response = client.get(
        f"/v1/datasets/{dataset_id}",
        headers=AUTH_HEADERS
    )

    assert response.status_code == 200
    assert response.json()["dataset_id"] == dataset_id
    assert response.json()["file_size_bytes"] > 0


# ---TEST DATASET DOWNLOAD---
def test_dataset_download():
    create_response = client.post(
        "/v1/datasets",
        json=VALID_PAYLOAD,
        headers=AUTH_HEADERS
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    response = client.get(
        f"/v1/datasets/{dataset_id}/download",
        headers=AUTH_HEADERS
    )

    assert response.status_code == 200

    # ---VERIFY SQLITE FILE HEADER---
    assert response.content.startswith(b"SQLite format 3")


# ---TEST MISSING DATASET---
def test_missing_dataset():
    missing_id = str(uuid4())

    response = client.get(
        f"/v1/datasets/{missing_id}",
        headers=AUTH_HEADERS
    )

    assert response.status_code == 404


# ---TEST INVALID DATASET ID---
def test_invalid_dataset_id():
    response = client.get(
        "/v1/datasets/not-a-valid-uuid",
        headers=AUTH_HEADERS
    )

    assert response.status_code == 422


# ---TEST GENERATION WITHOUT API KEY---
def test_generation_without_api_key():
    response = client.post(
        "/v1/datasets",
        json=VALID_PAYLOAD
    )

    assert response.status_code == 401


# ---TEST GENERATION WITH INVALID API KEY---
def test_generation_with_invalid_api_key():
    response = client.post(
        "/v1/datasets",
        json=VALID_PAYLOAD,
        headers={"X-API-Key": "incorrect-key"}
    )

    assert response.status_code == 401


# ---TEST METADATA WITHOUT API KEY---
def test_metadata_without_api_key():
    response = client.get(
        f"/v1/datasets/{uuid4()}"
    )

    assert response.status_code == 401


# ---TEST DOWNLOAD WITHOUT API KEY---
def test_download_without_api_key():
    response = client.get(
        f"/v1/datasets/{uuid4()}/download"
    )

    assert response.status_code == 401


# ---TEST DAILY GENERATION LIMIT---
def test_daily_generation_limit(monkeypatch):
    from fastapi import HTTPException

    request_count = 0

    def mock_quota(api_key):
        nonlocal request_count
        request_count += 1

        if request_count > 10:
            raise HTTPException(
                status_code=429,
                detail="Daily dataset generation limit reached"
            )

        return request_count

    monkeypatch.setattr(
        main,
        "consume_daily_quota",
        mock_quota
    )

    for attempt in range(1, 12):
        response = client.post(
            "/v1/datasets",
            json=VALID_PAYLOAD,
            headers=AUTH_HEADERS
        )

        if attempt <= 10:
            assert response.status_code == 201
        else:
            assert response.status_code == 429


# ---TEST GENERATION LOCK---
def test_generation_lock_rejects_busy_request():
    import main

    acquired = main.generation_lock.acquire(blocking=False)
    assert acquired, "Generation lock unexpectedly occupied"

    try:
        response = client.post(
            "/v1/datasets",
            json=VALID_PAYLOAD,
            headers=AUTH_HEADERS
        )

        assert response.status_code == 503
        assert "busy" in response.json()["detail"].lower()
        assert response.headers["retry-after"] == "5"

    finally:
        main.generation_lock.release()


# ---TEST DOWNLOAD REGISTRATION AND RELEASE---
def test_download_releases_tracking():
    import main

    # ---GENERATE TEST DATASET---
    create_response = client.post(
        "/v1/datasets",
        json=VALID_PAYLOAD,
        headers=AUTH_HEADERS
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]
    database_path = main.DATA_DIR / f"{dataset_id}.db"

    # ---DOWNLOAD DATASET---
    response = client.get(
        f"/v1/datasets/{dataset_id}/download",
        headers=AUTH_HEADERS
    )

    assert response.status_code == 200
    assert response.content.startswith(b"SQLite format 3")

    # ---VERIFY TRACKING WAS RELEASED---
    with main.download_lock:
        assert main.active_downloads.get(database_path, 0) == 0


# ---VERIFY SUCCESSFUL GENERATION LOGGING---
def test_successful_generation_is_logged(monkeypatch):
    captured_logs = []

    monkeypatch.setattr(
        main,
        "log_api_request",
        lambda **kwargs: captured_logs.append(kwargs)
    )

    response = client.post(
        "/v1/datasets",
        headers={"X-API-Key": TEST_API_KEY},
        json={
            "clients": 10,
            "employees": 5,
            "history_months": 1,
            "seed": 42
        }
    )

    assert response.status_code == 201
    assert len(captured_logs) == 1

    log = captured_logs[0]
    assert log["clients_requested"] == 10
    assert log["employees_requested"] == 5
    assert log["history_months"] == 1
    assert log["status_code"] == 201
    assert log["processing_seconds"] >= 0
    assert log["dataset_id"] == response.json()["dataset_id"]

    # ---VERIFY BUSY REQUEST LOGGING---
def test_busy_generation_is_logged(monkeypatch):
    captured_logs = []

    monkeypatch.setattr(
        main,
        "log_api_request",
        lambda **kwargs: captured_logs.append(kwargs)
    )

    main.generation_lock.acquire()

    try:
        response = client.post(
            "/v1/datasets",
            headers={"X-API-Key": TEST_API_KEY},
            json={
                "clients": 10,
                "employees": 5,
                "history_months": 1,
                "seed": 42
            }
        )
    finally:
        main.generation_lock.release()

    assert response.status_code == 503
    assert len(captured_logs) == 1
    assert captured_logs[0]["status_code"] == 503
    assert captured_logs[0]["error_code"] == "GENERATION_BUSY"

    # ---VERIFY QUOTA EXCEEDED LOGGING---
def test_quota_exceeded_is_logged(monkeypatch):
    captured_logs = []

    monkeypatch.setattr(
        main,
        "log_api_request",
        lambda **kwargs: captured_logs.append(kwargs)
    )

    def reject_quota(api_key):
        raise HTTPException(
            status_code=429,
            detail="Daily generation limit reached"
        )

    monkeypatch.setattr(
        main,
        "consume_daily_quota",
        reject_quota
    )

    response = client.post(
        "/v1/datasets",
        headers={"X-API-Key": TEST_API_KEY},
        json={
            "clients": 10,
            "employees": 5,
            "history_months": 1,
            "seed": 42
        }
    )

    assert response.status_code == 429
    assert len(captured_logs) == 1
    assert captured_logs[0]["status_code"] == 429
    assert captured_logs[0]["error_code"] == "QUOTA_EXCEEDED"