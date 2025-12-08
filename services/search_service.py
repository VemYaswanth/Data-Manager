import sqlite3
from fastapi import HTTPException

from core.config import DB_PATH
from services.embedding_service import semantic_search as _semantic_search
from services.file_service_db import get_file_by_id


# -------------------------------------------------------------
#   FULL TEXT SEARCH (keyword) — latest versions only
# -------------------------------------------------------------
def search_by_content(q: str, limit: int = 100):
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT f.id
        FROM file_index i
        JOIN files f ON f.id = i.file_id
        WHERE i.content LIKE ?
          AND f.is_latest = 1
        ORDER BY f.modified_at DESC
        LIMIT ?
        """,
        (f"%{q}%", limit),
    )

    ids = [row[0] for row in cur.fetchall()]
    conn.close()

    if not ids:
        raise HTTPException(status_code=404, detail="No files matched content search")

    results = []
    for fid in ids:
        f = get_file_by_id(fid)
        if f:
            results.append(f)

    return results


# -------------------------------------------------------------
#   SEMANTIC SEARCH (vector similarity)
# -------------------------------------------------------------
def search_by_semantic(q: str, top_k: int = 10):
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        hits = _semantic_search(q, top_k=top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not hits:
        raise HTTPException(status_code=404, detail="No semantic matches found")

    results = []
    for h in hits:
        f = get_file_by_id(h["file_id"])
        if f:
            results.append(
                {
                    **f,  # copy metadata
                    "score": h["score"],
                }
            )

    return results


# -------------------------------------------------------------
#   METADATA SEARCH (filename, extension, tags, project)
# -------------------------------------------------------------
def search_files(q=None, project_id=None, ext=None, tag=None, limit: int = 200):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    base_query = """
        SELECT 
            f.id,
            f.name,
            f.path,
            f.size,
            f.project_id,
            f.version,
            f.is_latest,
            f.created_at,
            f.modified_at
        FROM files f
    """

    joins = []
    where = []
    params = []

    # Tag filtering
    if tag:
        joins.append("JOIN file_tags t ON t.file_id = f.id")
        where.append("LOWER(t.tag) = ?")
        params.append(tag.lower().strip())

    # Project filtering
    if project_id is not None:
        where.append("f.project_id = ?")
        params.append(project_id)

    # Filename substring
    if q:
        where.append("LOWER(f.name) LIKE ?")
        params.append(f"%{q.lower()}%")

    # Extension filtering
    if ext:
        ext = ext.lower().lstrip(".")
        where.append("LOWER(f.name) LIKE ?")
        params.append(f"%.{ext}")

    # Only latest versions
    where.append("f.is_latest = 1")

    query = base_query
    if joins:
        query += " " + " ".join(joins)
    if where:
        query += " WHERE " + " AND ".join(where)

    query += " ORDER BY f.modified_at DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append(
            {
                "id": r[0],
                "name": r[1],
                "path": r[2],
                "size": r[3],
                "project_id": r[4],
                "version": r[5],
                "is_latest": bool(r[6]),
                "created_at": r[7],
                "modified_at": r[8],
            }
        )

    if not results:
        raise HTTPException(status_code=404, detail="No files matched search criteria")

    return results
