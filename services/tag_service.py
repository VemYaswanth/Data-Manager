import sqlite3
from datetime import datetime
from fastapi import HTTPException
from core.config import DB_PATH
from services.file_service_db import get_file_by_id


def add_tag(file_id: int, tag: str):
    tag = tag.strip().lower()
    if tag == "":
        raise HTTPException(status_code=400, detail="Tag cannot be empty")

    file = get_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Avoid exact duplicates
    cur.execute(
        "SELECT 1 FROM file_tags WHERE file_id = ? AND tag = ?",
        (file_id, tag),
    )
    if cur.fetchone():
        conn.close()
        return {"message": "Tag already exists"}

    now = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO file_tags (file_id, tag, created_at) VALUES (?, ?, ?)",
        (file_id, tag, now),
    )
    conn.commit()
    conn.close()

    return {"message": "Tag added", "tag": tag}


def remove_tag(file_id: int, tag: str):
    tag = tag.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM file_tags WHERE file_id = ? AND tag = ?",
        (file_id, tag),
    )
    deleted = cur.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Tag not found on file")

    return {"message": "Tag removed"}


def list_tags_for_file(file_id: int):
    file = get_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT tag FROM file_tags WHERE file_id = ? ORDER BY tag ASC",
        (file_id,),
    )
    rows = cur.fetchall()
    conn.close()

    return [r[0] for r in rows]
