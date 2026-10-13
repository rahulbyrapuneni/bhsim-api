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
        simulator.generate(database_path)

        validation = simulator.validate()

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
    "validation": validation
}