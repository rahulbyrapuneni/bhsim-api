
import time
from pathlib import Path
from threading import Lock

# ---CLEANUP CONFIGURATION---
DATASET_TTL_SECONDS = 3600


# ---DELETE EXPIRED DATASETS---
def cleanup_expired_datasets(
    data_dir: Path,
    download_lock: Lock | None = None,
    active_downloads: dict | None = None
) -> int:
    current_time = time.time()
    deleted_count = 0

    if not data_dir.exists():
        return 0

    if download_lock is None:
        raise ValueError("Download lock is required")

    if active_downloads is None:
        raise ValueError("Active download registry is required")

    # ---COORDINATE WITH ACTIVE DOWNLOADS---
    with download_lock:
        for database_path in data_dir.glob("*.db"):
            try:
                if active_downloads.get(database_path, 0) > 0:
                    continue

                file_age = current_time - database_path.stat().st_mtime

                if file_age >= DATASET_TTL_SECONDS:
                    database_path.unlink()
                    deleted_count += 1

            except FileNotFoundError:
                continue

    return deleted_count
