from fastapi.responses import FileResponse
from uuid import UUID
import time

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from bhsim import BHSimulator

# ---API CONFIGURATION---
app = FastAPI(
    title="BHSim API",
    description="API for generating synthetic behavioral health data",
    version="0.1.0"
)

DATA_DIR = Path("generated")
DATA_DIR.mkdir(exist_ok=True)

# ---REQUEST MODEL---
class DatasetRequest(BaseModel):
    clients: int = Field(default=100, ge=1, le=1000)
    employees: int = Field(default=20, ge=1, le=200)
    history_months: int = Field(default=12, ge=1, le=60)
    seed: int = 42

# ---HEALTH CHECK---
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "BHSim API",
        "version": "0.1.0"
    }

# ---GENERATE DATASET---
@app.post("/v1/datasets", status_code=201)
def create_dataset(request: DatasetRequest):
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
                # ---GENERATION TIMING---
        generation_start = time.perf_counter()
        simulator.generate(database_path)
        generation_seconds = time.perf_counter() - generation_start

        # ---VALIDATION TIMING---
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

# ---DATASET RETRIEVAL---
@app.get("/v1/datasets/{dataset_id}")
def get_dataset(dataset_id: UUID):
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
def download_dataset(dataset_id: UUID):
    database_path = DATA_DIR / f"{dataset_id}.db"

    if not database_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    return FileResponse(
        path=database_path,
        media_type="application/vnd.sqlite3",
        filename=f"bhsim-{dataset_id}.db"
    )