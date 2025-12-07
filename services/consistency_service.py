import os
from core.config import STORAGE_DIR, DB_PATH
import sqlite3

def check_consistency():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, path FROM files")
    rows = cur.fetchall()

    missing = []

    for file_id, path in rows:
        abs_path = os.path.join(STORAGE_DIR, path)
        if not os.path.exists(abs_path):
            missing.append(file_id)

    conn.close()
    return missing