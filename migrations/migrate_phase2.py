# migrations/migrate_phase2.py

import sqlite3
from core.config import DB_PATH
from datetime import datetime


def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Create projects table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    # 2. Add columns to files table (if missing)
    # SQLite doesn't support ADD COLUMN IF NOT EXISTS directly
    # So we check pragma table_info

    def column_exists(column_name):
        cur.execute("PRAGMA table_info(files);")
        columns = [row[1] for row in cur.fetchall()]
        return column_name in columns

    if not column_exists("project_id"):
        cur.execute("ALTER TABLE files ADD COLUMN project_id INTEGER;")

    if not column_exists("version"):
        cur.execute("ALTER TABLE files ADD COLUMN version INTEGER;")

    if not column_exists("is_latest"):
        cur.execute("ALTER TABLE files ADD COLUMN is_latest INTEGER;")

    # 3. Create default project if none exists
    cur.execute("SELECT COUNT(*) FROM projects;")
    project_count = cur.fetchone()[0]

    if project_count == 0:
        now = datetime.utcnow().isoformat()
        cur.execute("INSERT INTO projects (name, created_at) VALUES (?, ?)",
                    ("Default Project", now))

    # Get the new default project id
    cur.execute("SELECT id FROM projects WHERE name=?", ("Default Project",))
    default_project_id = cur.fetchone()[0]

    # 4. Assign existing files to default project + set versioning values
    cur.execute("UPDATE files SET project_id=?, version=1, is_latest=1 WHERE project_id IS NULL",
                (default_project_id,))

    conn.commit()
    conn.close()

    print("Phase 2 migration successful!")


if __name__ == "__main__":
    run_migration()
