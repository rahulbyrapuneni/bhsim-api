# BHSim API

A REST API for generating and validating synthetic behavioral health datasets using the open-source [BHSim](https://github.com/rahulbyrapuneni/bhsim) Python library.

## Overview

BHSim API makes synthetic dataset generation accessible through HTTP requests. Applications can request reproducible behavioral health datasets without implementing the underlying generation logic.

The API is built using FastAPI and integrates the published BHSim Python package.

## Features

- Generate synthetic behavioral health datasets through an API.
- Configure individual counts, employee counts, history duration, and random seed.
- Validate generated datasets using BHSim's built-in validator.
- Generate SQLite database files with unique dataset identifiers.
- Automatically validate API request parameters.
- Explore endpoints through interactive Swagger documentation.
- Run automated tests using pytest.

## Architecture

Client Application → FastAPI → BHSim Library → SQLite Dataset → Validation → API Response

## Requirements

- Python 3.10+ (subject to the installed BHSim package's Python requirements)
- FastAPI
- Uvicorn
- BHSim 1.0.1
- pytest
- httpx

## Installation

Clone the repository:

```bash
git clone https://github.com/rahulbyrapuneni/bhsim-api.git
cd bhsim-api
```

Create a virtual environment:

```bash
python -m venv .venv
```

Install dependencies using the virtual environment's Python executable:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the server:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

### GET /health

Checks whether the API server is responding.

### POST /v1/datasets

Generates and validates a synthetic SQLite dataset.

Example request:

```json
{
  "clients": 100,
  "employees": 20,
  "history_months": 12,
  "seed": 42
}
```

Example successful response:

```json
{
  "dataset_id": "generated-uuid",
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

A successful request returns HTTP status **201 Created**.

Generated databases are saved locally inside the `generated/` directory.

Dataset download and retrieval endpoints are planned for a future release.

## Testing

Run the automated tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The initial test suite covers the health endpoint, input validation, and dataset generation.

## Current Limitations

- Dataset generation is synchronous.
- Files are stored locally.
- Authentication and rate limiting are not yet implemented.
- The service is intended for local development and testing, not unrestricted public deployment.

## Roadmap

- Dataset metadata retrieval and downloads.
- Improved file management.
- Docker deployment.
- Automated testing with GitHub Actions.
- Integration with AI workflows and other services.

## Related Project

[BHSim — Synthetic Behavioral Health Data Library](https://github.com/rahulbyrapuneni/bhsim)

## Maintainer

Rahul Byrapuneni