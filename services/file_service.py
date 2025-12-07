import sqlite3
from core.config import DB_PATH

def get_all_files():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, path, size, created_at, modified_at FROM files")
    rows = cur.fetchall()
    conn.close()

    files = []
    for r in rows:
        files.append({
            "id": r[0],
            "name": r[1],
            "path": r[2],
            "size": r[3],
            "created_at": r[4],
            "modified_at": r[5],
        })
    return files
