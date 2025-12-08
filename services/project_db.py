# services/project_db.py

import sqlite3
from datetime import datetime
from core.config import DB_PATH


def create_project(name: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    cur.execute(
        "INSERT INTO projects (name, created_at) VALUES (?, ?)",
        (name, now)
    )

    conn.commit()
    project_id = cur.lastrowid
    conn.close()

    return project_id


def get_all_projects():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, name, created_at FROM projects ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()

    projects = [
        {"id": r[0], "name": r[1], "created_at": r[2]}
        for r in rows
    ]
    return projects


def get_project_by_id(project_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, name, created_at FROM projects WHERE id=?", (project_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        return {"id": row[0], "name": row[1], "created_at": row[2]}
    return None


def delete_project_from_db(project_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    conn.close()
