from fastapi.responses import FileResponse
from uuid import UUID
import time
import os
import secrets
from threading import Lock
from fastapi.responses import StreamingResponse
from quota import consume_daily_quota
from cleanup import cleanup_expired_datasets
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from threading import Lock
from pathlib import Path
from uuid import uuid4
from pydantic import BaseModel, Field
from bhsim import BHSimulator

# ---API CONFIGURATION---
app = FastAPI(
    title="BHSim API",
    description="API for generating synthetic behavioral health data",
    version="0.2.0"
)

DATA_DIR = Path("generated")
DATA_DIR.mkdir(exist_ok=True)

# ---GENERATION CONCURRENCY CONTROL---
generation_lock = Lock()

# ---ACTIVE DOWNLOAD TRACKING---
download_lock = Lock()
active_downloads = {}

# ---API KEY AUTHENTICATION---
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)

def verify_api_key(api_key: str | None = Security(api_key_header)):
    expected_key = os.getenv("BHSIM_API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured"
        )

    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

    return api_key

# ---REQUEST MODEL---
class DatasetRequest(BaseModel):
    clients: int = Field(default=100, ge=1, le=500)
    employees: int = Field(default=20, ge=1, le=100)
    history_months: int = Field(default=12, ge=1, le=12)
    seed: int = 42

# ---HEALTH CHECK---
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "BHSim API",
        "version": "0.2.0"
    }

# ---GENERATE DATASET---
@app.post("/v1/datasets", status_code=201)

def create_dataset(
    request: DatasetRequest,
    api_key: str = Depends(verify_api_key)
):
    # ---ALLOW ONE ACTIVE GENERATION---
    if not generation_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=503,
            detail="Dataset generation is busy. Please retry shortly.",
            headers={"Retry-After": "5"}
        )

    try:
        # ---CLEANUP EXPIRED DATASETS---
        cleanup_expired_datasets(
        DATA_DIR,
        download_lock,
        active_downloads
        )

        # ---ENFORCE DAILY QUOTA---
        consume_daily_quota(api_key)

        dataset_id = str(uuid4())
        database_path = DATA_DIR / f"{dataset_id}.db"

        simulator = BHSimulator(
            clients=request.clients,
            employees=request.employees,
            history_months=request.history_months,
            seed=request.seed
        )

        # ---GENERATE AND VALIDATE DATASET---
        try:
            generation_start = time.perf_counter()
            simulator.generate(database_path)
            generation_seconds = time.perf_counter() - generation_start

            validation_start = time.perf_counter()
            validation = simulator.validate()
            validation_seconds = time.perf_counter() - validation_start

            if not validation.get("valid", False):
                database_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=500,
                    detail={
                        "message": "Generated dataset failed validation",
                        "issues": validation.get("issues", [])
                    }
                )

        except HTTPException:
            raise

        except Exception:
            database_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=500,
                detail="Dataset generation or validation failed"
            )

        return {
            "dataset_id": dataset_id,
            "status": "completed",
            "clients_requested": request.clients,
            "employees_requested": request.employees,
            "database_format": "sqlite",
            "validation": validation,
            "performance": {
                "generation_seconds": round(generation_seconds, 3),
                "validation_seconds": round(validation_seconds, 3),
                "total_processing_seconds": round(
                    generation_seconds + validation_seconds, 3
                )
            }
        }

    finally:
        # ---ALWAYS RELEASE GENERATION LOCK---
        generation_lock.release()


# ---DATASET RETRIEVAL---
@app.get("/v1/datasets/{dataset_id}")
def get_dataset(
    dataset_id: UUID,api_key: str = Depends(verify_api_key)):
    database_path = DATA_DIR / f"{dataset_id}.db"

    if not database_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    return {
        "dataset_id": str(dataset_id),
        "status": "completed",
        "database_format": "sqlite",
        "file_size_bytes": database_path.stat().st_size
    }


# ---DATASET DOWNLOAD---

@app.get("/v1/datasets/{dataset_id}/download")
def download_dataset(
    dataset_id: UUID,
    api_key: str = Depends(verify_api_key)
):
    database_path = DATA_DIR / f"{dataset_id}.db"

    # ---REGISTER ACTIVE DOWNLOAD---
    with download_lock:
        if not database_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        active_downloads[database_path] = active_downloads.get(database_path, 0) + 1

    # ---STREAM DATASET---
    def stream_file():
        try:
            with open(database_path, "rb") as file:
                while chunk := file.read(1024 * 1024):
                    yield chunk
        finally:
            # ---RELEASE DOWNLOAD REGISTRATION---
            with download_lock:
                active_downloads[database_path] -= 1

                if active_downloads[database_path] == 0:
                    del active_downloads[database_path]

    return StreamingResponse(
        stream_file(),
        media_type="application/vnd.sqlite3",
        headers={
            "Content-Disposition":
                f'attachment; filename="bhsim-{dataset_id}.db"'
        }
    )
