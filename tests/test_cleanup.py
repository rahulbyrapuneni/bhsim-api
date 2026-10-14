
import os
import time
from threading import Lock

from cleanup import cleanup_expired_datasets

# ---TEST EXPIRED DATASET CLEANUP---
def test_cleanup_expired_datasets(tmp_path):
    old_file = tmp_path / "old_dataset.db"
    new_file = tmp_path / "new_dataset.db"
    other_file = tmp_path / "notes.txt"

    old_file.write_bytes(b"old dataset")
    new_file.write_bytes(b"new dataset")
    other_file.write_text("Do not delete")

    # ---MAKE ONE FILE TWO HOURS OLD---
    old_time = time.time() - 7200
    os.utime(old_file, (old_time, old_time))

    download_lock = Lock()
    active_downloads = {}

    deleted = cleanup_expired_datasets(
        tmp_path,
        download_lock,
        active_downloads
    )

    assert deleted == 1
    assert not old_file.exists()
    assert new_file.exists()
    assert other_file.exists()


# ---TEST ACTIVE DOWNLOAD PROTECTION---
def test_cleanup_preserves_active_download(tmp_path):
    database_file = tmp_path / "active_dataset.db"
    database_file.write_bytes(b"active dataset")

    old_time = time.time() - 7200
    os.utime(database_file, (old_time, old_time))

    download_lock = Lock()
    active_downloads = {database_file: 2}

    # ---FILE MUST SURVIVE WHILE DOWNLOADING---
    deleted = cleanup_expired_datasets(
        tmp_path,
        download_lock,
        active_downloads
    )

    assert deleted == 0
    assert database_file.exists()

    # ---SIMULATE BOTH DOWNLOADS FINISHING---
    with download_lock:
        del active_downloads[database_file]

    deleted = cleanup_expired_datasets(
        tmp_path,
        download_lock,
        active_downloads
    )

    assert deleted == 1
    assert not database_file.exists()
