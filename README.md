# BHSim API

**A REST API for generating, validating, and downloading synthetic behavioral health datasets.**

Built with FastAPI and powered by [BHSim](https://github.com/rahulbyrapuneni/bhsim), an open-source Python library for generating connected synthetic behavioral health data.

BHSim API makes synthetic dataset generation accessible to applications, analytical workflows, testing environments, and future AI agents through HTTP requests.

## Overview

BHSim API provides a lightweight service for generating realistic, interconnected synthetic behavioral health datasets without requiring users to directly interact with the underlying Python library.

It converts the functionality of BHSim into a REST interface that can be consumed by other software systems.

The service supports:

- Synthetic SQLite dataset generation
- Configurable simulation parameters
- Automated data validation
- Dataset metadata retrieval
- SQLite database downloads
- Containerized deployment using Docker
- Persistent dataset storage
- Automated API testing

**All generated records are synthetic. The API does not require real patient information or protected health information (PHI).**

## Architecture

```text
Client Application / API Consumer
              |
              v
        FastAPI Service
              |
              v
       Request Validation
              |
              v
       BHSim Python Library
              |
              v
       Synthetic Data Engine
              |
              v
        SQLite Database
              |
              v
       Dataset Validation
              |
              v
       Dataset Storage
              |
              v
    API Response / Download
```

The architecture separates HTTP request handling from the synthetic data-generation engine.

BHSim remains an independent Python library, while BHSim API exposes its functionality as an HTTP service.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| FastAPI | REST API framework |
| Pydantic | Request validation |
| BHSim 1.0.1 | Synthetic data generation |
| SQLite | Generated relational databases |
| Uvicorn | ASGI application server |
| Pytest | Automated testing |
| HTTPX | API testing support |
| Docker | Containerized application deployment |
| Docker Volumes | Persistent dataset storage |
| Git / GitHub | Version control and source distribution |

## Features

### 1. Synthetic Dataset Generation

Generate behavioral health datasets through HTTP requests.

Supported configuration parameters include:

| Parameter | Default | Description |
|---|---:|---|
| `clients` | 100 | Number of synthetic individuals |
| `employees` | 20 | Number of synthetic employees |
| `history_months` | 12 | Number of historical months |
| `seed` | 42 | Random seed for reproducibility |

The API validates request parameters before invoking the generation engine.

### 2. Data Validation

Each generated dataset is checked using BHSim's built-in validation functionality.

The API reports successful generation only when the library's validation passes.

Example:

```json
{
  "validation": {
    "valid": true,
    "issues": []
  }
}
```

Validation failures are returned as API errors.

### 3. Dataset Retrieval

Retrieve metadata about a previously generated dataset using its unique identifier.

### 4. Dataset Download

Download generated SQLite databases through an HTTP endpoint.

The downloaded database can be used with SQLite-compatible tools, SQL clients, analytical applications, and development workflows.

### 5. Docker Deployment

Run the application inside a Docker container with Python and application dependencies packaged together.

### 6. Persistent Storage

Generated SQLite files can be stored in a named Docker volume so that datasets survive container removal and recreation.

## Project Structure

```text
bhsim-api/
├── main.py
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
├── README.md
├── tests/
│   └── test_api.py
└── generated/            # Created at runtime; excluded from Git
```

The local `.venv/` directory is also excluded from version control.

## Installation

### Prerequisites

- A compatible Python installation
- Git
- Docker Desktop (optional for local Python development)

The current Docker image uses Python 3.14.

### 1. Clone the Repository

```bash
git clone https://github.com/rahulbyrapuneni/bhsim-api.git
cd bhsim-api
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

### 3. Install Dependencies

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Start the API Server

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

The development server will start at:

http://127.0.0.1:8000

### 5. Access API Documentation

Open:

http://127.0.0.1:8000/docs

FastAPI automatically generates interactive Swagger UI documentation for the available endpoints.

The OpenAPI specification is also available at:

http://127.0.0.1:8000/openapi.json

## API Reference

### GET /health

Checks whether the API service is responding.

**Example response — HTTP 200**

```json
{
  "status": "healthy",
  "service": "BHSim API",
  "version": "0.1.0"
}
```

This endpoint verifies API responsiveness. It is not a complete dependency or database health check.

### POST /v1/datasets

Generates and validates a synthetic behavioral health dataset.

**Example request**

```json
{
  "clients": 100,
  "employees": 20,
  "history_months": 12,
  "seed": 42
}
```

**Example response — HTTP 201 Created**

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

A unique dataset identifier is generated for each successful request.

**Possible responses**

| HTTP Code | Meaning |
|---|---|
| 201 | Dataset successfully created |
| 422 | Invalid request parameters |
| 500 | Dataset generation or validation failed |

### GET /v1/datasets/{dataset_id}

Retrieves metadata for a previously generated dataset.

**Example request**

```http
GET /v1/datasets/e834482a-a6f5-4812-bd93-149bd14928f3
```

**Example response — HTTP 200**

```json
{
  "dataset_id": "e834482a-a6f5-4812-bd93-149bd14928f3",
  "status": "completed",
  "database_format": "sqlite",
  "file_size_bytes": 1234567
}
```

The file size above is illustrative and varies by dataset.

Returns HTTP 404 if the requested dataset does not exist, or HTTP 422 if the identifier is malformed.

### GET /v1/datasets/{dataset_id}/download

Downloads the generated SQLite database.

**Example request**

```http
GET /v1/datasets/e834482a-a6f5-4812-bd93-149bd14928f3/download
```

**Successful response — HTTP 200**

Returns a SQLite database file.

Example downloaded filename:

```text
bhsim-e834482a-a6f5-4812-bd93-149bd14928f3.db
```

Returns HTTP 404 if the dataset does not exist.

## Docker Deployment

Docker allows BHSim API to run in an isolated environment with its required dependencies.

### 1. Build the Docker Image

From the repository root:

```powershell
docker build -t bhsim-api:0.1 .
```

### 2. Run the Container

```powershell
docker run -d --name bhsim-api-container -p 127.0.0.1:8000:8000 -v bhsim-data:/app/generated bhsim-api:0.1
```

This command:

- Runs the API in the background.
- Makes the API available on localhost port 8000.
- Creates or reuses the named Docker volume `bhsim-data`.
- Stores generated databases outside the container's temporary filesystem.

### 3. Verify the Container

```powershell
docker ps
```

Open:

http://127.0.0.1:8000/docs

### 4. View Container Logs

```powershell
docker logs bhsim-api-container
```

### 5. Stop the Container

```powershell
docker stop bhsim-api-container
```

### 6. Start the Existing Container

```powershell
docker start bhsim-api-container
```

### 7. Remove the Container

First stop it, then run:

```powershell
docker rm bhsim-api-container
```

Removing the container does not automatically remove the named Docker volume.

### 8. Recreate the Container with Existing Data

```powershell
docker run -d --name bhsim-api-container -p 127.0.0.1:8000:8000 -v bhsim-data:/app/generated bhsim-api:0.1
```

Because the same volume is mounted, previously generated SQLite databases remain available.

**Note:** Removing the Docker volume itself would delete the datasets stored in that volume.

## Data Persistence Verification

Persistent storage was manually verified using the following process:

1. Generate a dataset through `POST /v1/datasets`.
2. Save the generated dataset ID.
3. Stop and remove the Docker container.
4. Recreate the container using the same named Docker volume.
5. Request the previously generated dataset using `GET /v1/datasets/{dataset_id}`.

The existing dataset remained accessible and returned HTTP 200 after the container was recreated.

This demonstrates persistence across container replacement on the same Docker host.

## Automated Testing

BHSim API currently includes seven automated tests.

| Test | Expected Behavior |
|---|---|
| Health endpoint | Returns HTTP 200 |
| Invalid client count | Returns HTTP 422 |
| Dataset generation | Returns HTTP 201 and passes validation |
| Dataset retrieval | Returns HTTP 200 and file metadata |
| Dataset download | Returns HTTP 200 with a SQLite file header |
| Missing dataset | Returns HTTP 404 |
| Invalid dataset ID | Returns HTTP 422 |

Run all tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

**Current verified result: 7 tests passed.**

These tests verify the implemented API behavior and selected validation conditions. They are not a substitute for full security, concurrency, or production load testing.

## Example Generated Dataset

During local development, one test configuration used:

```json
{
  "clients": 100,
  "employees": 20,
  "history_months": 12,
  "seed": 42
}
```

The generated database contained:

| Entity | Records |
|---|---:|
| Individuals | 100 |
| Employees | 20 |
| Programs | 8 |
| Visits | 1,477 |
| Assessments | 390 |

The database contained 18 tables.

SQLite's `PRAGMA foreign_key_check` reported zero violations, and BHSim's built-in validation returned:

```json
{
  "valid": true,
  "issues": []
}
```

These are results from one development test, not guaranteed counts for every configuration.

## Current Limitations

BHSim API is currently a development-stage service.

- Dataset generation executes synchronously.
- Generated files are stored on the local filesystem or in a Docker volume.
- There is no authentication or tenant isolation.
- There is no rate limiting or dataset expiration.
- Generation resource limits are basic.
- Metadata is derived from stored files rather than a dedicated metadata database.
- Production monitoring and distributed job execution are not implemented.
- No public production deployment has been completed.

**Do not expose the current service directly to the public internet without additional security and operational controls.**

## Development Roadmap

### Completed

- [x] FastAPI service
- [x] BHSim package integration
- [x] Request validation
- [x] Synthetic SQLite dataset generation
- [x] Built-in dataset validation
- [x] Dataset metadata retrieval
- [x] SQLite dataset downloads
- [x] Seven automated API tests
- [x] Docker image build
- [x] Docker container execution
- [x] Persistent Docker volume verification

### Planned

- [ ] GitHub Actions CI/CD
- [ ] Automated Docker build verification
- [ ] Improved API error handling and logging
- [ ] Expanded tests and isolated test storage
- [ ] Dataset retention and cleanup controls
- [ ] API authentication and request limits
- [ ] Deployment configuration improvements
- [ ] Integration with external services and AI workflows

## Future AI Integration

BHSim API is intended to serve as a reusable synthetic-data service for future AI engineering projects.

Potential integrations include:

- AI workflow development and testing
- SQL-based analytical applications
- Tool-using AI agents
- API integration demonstrations
- Evaluation of AI applications using synthetic relational data

This API is a foundational engineering component rather than an AI model or autonomous AI agent.

## Related Projects

**BHSim Python Library**

https://github.com/rahulbyrapuneni/bhsim

**BHSim API**

https://github.com/rahulbyrapuneni/bhsim-api

## Author and Maintainer

**Rahul Byrapuneni**

Open-source software development focused on synthetic data, data integration, AI engineering, and enterprise deployment.

## License

See the repository's license information when a license is added. No separate license is declared for this API repository in this documentation.