import sqlite3
from core.config import DB_PATH

def get_storage_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT project_id, SUM(size)
        FROM files
        GROUP BY project_id
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {"project_id": r[0], "total_size": r[1] or 0}
        for r in rows
    ]


def get_version_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT name, COUNT(*)
        FROM files
        GROUP BY name
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {"file": r[0], "version_count": r[1]}
        for r in rows
    ]


def get_daily_activity():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT DATE(timestamp), COUNT(*)
        FROM audit_log
        GROUP BY DATE(timestamp)
        ORDER BY DATE(timestamp)
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {"date": r[0], "events": r[1]}
        for r in rows
    ]
