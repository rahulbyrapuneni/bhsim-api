
import os
import hashlib
import psycopg

from fastapi import HTTPException

# ---QUOTA CONFIGURATION---
DAILY_LIMIT = 10


# ---CHECK AND CONSUME DAILY QUOTA---
def consume_daily_quota(api_key: str):
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise HTTPException(
            status_code=503,
            detail="Quota database is not configured"
        )

    # ---IDENTIFY API KEY WITHOUT STORING SECRET---
    api_key_id = hashlib.sha256(
        api_key.encode("utf-8")
    ).hexdigest()

    try:
        with psycopg.connect(
            database_url,
            connect_timeout=10
        ) as conn:

            # ---ATOMIC QUOTA UPDATE---
            result = conn.execute(
                """
                INSERT INTO api_daily_usage (
                    api_key_id,
                    usage_date,
                    request_count,
                    updated_at
                )
                VALUES (
                    %s,
                    (NOW() AT TIME ZONE 'UTC')::date,
                    1,
                    NOW()
                )
                ON CONFLICT (api_key_id, usage_date)
                DO UPDATE SET
                    request_count =
                        api_daily_usage.request_count + 1,
                    updated_at = NOW()
                WHERE api_daily_usage.request_count < %s
                RETURNING request_count
                """,
                (api_key_id, DAILY_LIMIT)
            ).fetchone()

            if result is None:
                raise HTTPException(
                    status_code=429,
                    detail="Daily dataset generation limit reached"
                )

            return result[0]

    except HTTPException:
        raise

    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Quota service temporarily unavailable"
        )
