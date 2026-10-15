
import os
import logging
import hashlib
import psycopg

# ---LOGGER CONFIGURATION---
logger = logging.getLogger(__name__)


# ---RECORD API REQUEST---
def log_api_request(
    api_key=None,
    dataset_id=None,
    clients_requested=None,
    employees_requested=None,
    history_months=None,
    status_code=500,
    generation_seconds=None,
    validation_seconds=None,
    processing_seconds=None,
    error_code=None
):
    # ---IDENTIFY API KEY WITHOUT STORING SECRET---
    api_key_id = (
        hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        if api_key else None
    )

    # ---CONNECT TO NEON---
    try:
        database_url = os.environ["DATABASE_URL"]

        with psycopg.connect(
            database_url,
            connect_timeout=5
        ) as conn:
            conn.execute(
                """
                INSERT INTO api_request_logs (
                    api_key_id,
                    dataset_id,
                    clients_requested,
                    employees_requested,
                    history_months,
                    status_code,
                    generation_seconds,
                    validation_seconds,
                    processing_seconds,
                    error_code
                )
                VALUES (%s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s)
                """,
                (
                    api_key_id,
                    dataset_id,
                    clients_requested,
                    employees_requested,
                    history_months,
                    status_code,
                    generation_seconds,
                    validation_seconds,
                    processing_seconds,
                    error_code
                )
            )

    except (psycopg.Error, KeyError):
        # ---LOGGING MUST NOT INTERRUPT API OPERATIONS---
        logger.warning(
            "Failed to write API request log",
            exc_info=True
        )
