# services/consistency_service.py

import os
from core.config import STORAGE_DIR
from services.file_service_db import get_all_files, delete_file_metadata


# -------------------------------------------------------
# 1. DB → Disk Consistency Check
# -------------------------------------------------------

def find_missing_files():
    """
    Returns DB entries whose file does NOT exist on disk.
    """
    missing = []
    for f in get_all_files():
        abs_path = STORAGE_DIR / f["path"]
        if not abs_path.exists():
            missing.append(f)
    return missing


# -------------------------------------------------------
# 2. Disk → DB Consistency Check (orphan files)
# -------------------------------------------------------

def find_orphan_files():
    """
    Returns disk files that are NOT referenced in DB.
    """
    db_paths = {f["path"] for f in get_all_files()}
    orphaned = []

    for root, dirs, files in os.walk(STORAGE_DIR):
        for fname in files:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, STORAGE_DIR)
            if rel not in db_paths:
                orphaned.append(rel)

    return orphaned


# -------------------------------------------------------
# 3. Simple consistency summary (used by /consistency)
# -------------------------------------------------------

def check_consistency():
    """
    Returns only the missing DB entries (no orphan cleanup).
    """
    return [f["id"] for f in find_missing_files()]


# -------------------------------------------------------
# 4. Full auto-repair (called by /repair/full)
# -------------------------------------------------------

def auto_repair():
    """
    Repairs:
      - missing DB entries (removes broken rows)
      - orphan disk files (removes them)
    """
    missing = find_missing_files()
    orphaned = find_orphan_files()

    repaired = {
        "cleared_missing_db": 0,
        "removed_orphans": 0
    }

    # Remove DB entries for missing files
    for f in missing:
        delete_file_metadata(f["id"])
        repaired["cleared_missing_db"] += 1

    # Remove orphan disk files
    for rel in orphaned:
        abs_path = STORAGE_DIR / rel
        try:
            abs_path.unlink()
            repaired["removed_orphans"] += 1
        except:
            pass

    return repaired
