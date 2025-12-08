import sqlite3
from core.config import DB_PATH


def insert_file_metadata(name, path, size, created_at, modified_at,
                         project_id, version, is_latest):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO files 
        (name, path, size, created_at, modified_at, project_id, version, is_latest)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        path,
        size,
        created_at,
        modified_at,
        project_id,
        version,
        is_latest
    ))

    conn.commit()
    conn.close()


def delete_file_metadata(file_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM files WHERE id = ?", (file_id,))
    conn.commit()
    conn.close()


def get_file_by_id(file_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, path, size, created_at, modified_at,
               project_id, version, is_latest
        FROM files WHERE id = ?
    """, (file_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None
    
    return {
        "id": row[0],
        "name": row[1],
        "path": row[2],
        "size": row[3],
        "created_at": row[4],
        "modified_at": row[5],
        "project_id": row[6],
        "version": row[7],
        "is_latest": row[8],
    }


def get_all_files():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, path, size, created_at, modified_at,
               project_id, version, is_latest
        FROM files
    """)

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
            "project_id": r[6],
            "version": r[7],
            "is_latest": r[8],
        })

    return files

def get_project_files_latest(project_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, path, size, created_at, modified_at,
               project_id, version, is_latest
        FROM files
        WHERE project_id = ? AND is_latest = 1
        ORDER BY name
    """, (project_id,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "name": r[1],
            "path": r[2],
            "size": r[3],
            "created_at": r[4],
            "modified_at": r[5],
            "project_id": r[6],
            "version": r[7],
            "is_latest": r[8],
        }
        for r in rows
    ]


def get_file_versions(project_id, filename):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, path, size, created_at, modified_at,
               project_id, version, is_latest
        FROM files
        WHERE project_id = ? AND name = ?
        ORDER BY version DESC
    """, (project_id, filename))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "name": r[1],
            "path": r[2],
            "size": r[3],
            "created_at": r[4],
            "modified_at": r[5],
            "project_id": r[6],
            "version": r[7],
            "is_latest": r[8],
        }
        for r in rows
    ]
