import sqlite3
from core.config import DB_PATH

def add_search_index(file_id: int, text: str, embedding: list):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO search_index (file_id, text_content, embedding)
        VALUES (?, ?, ?)
    """, (file_id, text, ",".join(map(str, embedding))))

    conn.commit()
    conn.close()


def search_by_file_id(file_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT text_content FROM search_index WHERE file_id = ?", (file_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else None


def get_all_search_embeddings():
    """
    Returns: [(file_id, embedding_vector_as_list), ...]
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT file_id, embedding FROM search_index")
    rows = cur.fetchall()
    conn.close()

    vectors = []
    for fid, emb in rows:
        if emb:
            vectors.append((fid, list(map(float, emb.split(",")))))
    return vectors
