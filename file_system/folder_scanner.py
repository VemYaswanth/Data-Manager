import os
import sqlite3
from datetime import datetime
from core.config import STORAGE_DIR, DB_PATH

def scan_and_index():
    """
    Scans STORAGE_DIR recursively,
    extracts metadata, saves/updates them in SQLite.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for root, dirs, files in os.walk(STORAGE_DIR):
        for filename in files:
            file_path = os.path.join(root, filename)
            stat = os.stat(file_path)

            name = filename
            path = os.path.relpath(file_path, STORAGE_DIR)
            size = stat.st_size
            created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
            modified_at = datetime.fromtimestamp(stat.st_mtime).isoformat()

            # Check if file already exists in DB
            cur.execute("SELECT id FROM files WHERE path = ?", (path,))
            existing = cur.fetchone()

            if existing:
                # Update record
                cur.execute("""
                    UPDATE files
                    SET size=?, modified_at=?
                    WHERE id=?
                """, (size, modified_at, existing[0]))
            else:
                # Insert new record
                cur.execute("""
                    INSERT INTO files (name, path, size, created_at, modified_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, path, size, created_at, modified_at))

    conn.commit()
    conn.close()
