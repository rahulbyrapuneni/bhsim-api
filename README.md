# BHSim API

**A REST API for generating, validating, and downloading synthetic behavioral health datasets.**

[![CI](https://github.com/rahulbyrapuneni/bhsim-api/actions/workflows/ci.yml/badge.svg)](https://github.com/rahulbyrapuneni/bhsim-api/actions)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)

Built with FastAPI and powered by [BHSim](https://github.com/rahulbyrapuneni/bhsim), an open-source Python library for generating interconnected synthetic behavioral health data.

BHSim API exposes the library through HTTP, allowing external applications, data platforms, and AI workflows to generate and retrieve synthetic datasets without directly integrating Python generation code.

## Features

- Generate synthetic relational datasets through REST endpoints.
- Configure client count, employee count, history duration, and random seed.
- Validate generated data using BHSim's built-in validator.
- Retrieve dataset metadata and download SQLite databases.
- Run the API in Docker with persistent dataset storage.
- Automatically run tests, Docker builds, and smoke tests through GitHub Actions.

## Architecture

```text
Client Application
       |
       v
   FastAPI
       |
       v
Input Validation
       |
       v
  BHSim Library
       |
       v
SQLite Generation
       |
       v
Data Validation
       |
       v
Storage / Download
```

**Tech stack:** Python · FastAPI · Pydantic · BHSim · SQLite · Pytest · Docker · GitHub Actions

## Quick Start

### Run locally

```powershell
git clone https://github.com/rahulbyrapuneni/bhsim-api.git
cd bhsim-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

### Run with Docker

```powershell
docker build -t bhsim-api:0.1 .
docker run -d --name bhsim-api-container -p 127.0.0.1:8000:8000 -v bhsim-data:/app/generated bhsim-api:0.1
```

**Interactive API documentation:** http://127.0.0.1:8000/docs

Docker volumes preserve generated datasets across container removal and recreation, provided the volume is retained.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API responsiveness |
| POST | `/v1/datasets` | Generate and validate a dataset |
| GET | `/v1/datasets/{dataset_id}` | Retrieve dataset metadata |
| GET | `/v1/datasets/{dataset_id}/download` | Download the SQLite database |

### Example Request

**POST `/v1/datasets`**

```json
{
  "clients": 100,
  "employees": 20,
  "history_months": 12,
  "seed": 42
}
```

**Example successful response — HTTP 201**

```json
{
  "dataset_id": "e834482a-a6f5-4812-bd93-149bd14928f3",
  "status": "completed",
  "clients_requested": 100,
  "employees_requested": 20,
  "database_format": "sqlite",
  "validation": {
    "valid": true,
    "issues": []
  }
}
```

Each generated dataset receives a unique identifier that can be used for metadata retrieval and downloads.

## Testing & Continuous Integration

Run the tests locally:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

**Verified milestones:**

- 7 automated API tests passed.
- Docker image built and API executed successfully.
- Dataset persistence verified across container recreation.
- GitHub Actions API tests and Docker smoke test passed.

The [GitHub Actions workflow](https://github.com/rahulbyrapuneni/bhsim-api/actions) automatically runs tests, builds the Docker image, and checks that the containerized API responds to `/health`.

## Development Status

**v0.1.0 — Initial development milestone complete.**

The API has been tested locally and in Docker. It is not yet intended for unrestricted public deployment.

Production hardening, including authentication, rate limiting, dataset cleanup, and operational monitoring, remains future work.

## AI Engineering Journey

BHSim API is **Chapter 2** of a connected open-source engineering portfolio exploring the journey from synthetic data generation to deployed enterprise AI.

| Chapter | Project | Purpose | Status |
|---|---|---|---|
| 1 | [BHSim](https://github.com/rahulbyrapuneni/bhsim) | Generate synthetic relational data | Completed |
| 2 | **BHSim API** | Expose data generation through HTTP | Completed |
| 3 | BridgeKit | Connect databases and external APIs | Planned |
| 4 | ActionFlow | Add AI tool calling and controlled workflows | Planned |
| 5 | AI Evaluation & Observability | Test, trace, and measure AI behavior | Planned |
| 6 | FieldOps AI | Deliver an integrated customer-facing AI solution | Planned |

Each chapter adds a specific engineering capability, ultimately contributing to a deployable AI system designed around real customer integration requirements.

## Author

**Rahul Byrapuneni**

[GitHub](https://github.com/rahulbyrapuneni) · [Portfolio](https://rahul-portfolio-phi-azure.vercel.app/)

## License

The API repository does not currently declare a separate license. The underlying BHSim library is maintained as an independent open-source project.