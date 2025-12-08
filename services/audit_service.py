import sqlite3
from datetime import datetime
from core.config import DB_PATH


def log_event(action: str, project_id=None, file=None, version=None, meta=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    timestamp = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO audit_log (action, project_id, file, version, meta, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (action, project_id, file, version, meta, timestamp))

    conn.commit()
    conn.close()
