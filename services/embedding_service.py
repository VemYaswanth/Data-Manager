# services/embedding_service.py

import json
from datetime import datetime

import sqlite3
from core.config import DB_PATH

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _model = SentenceTransformer(MODEL_NAME)
except Exception:
    _model = None
    np = None


def _ensure_model():
    if _model is None:
        raise RuntimeError(
            "Semantic model not available. Install sentence-transformers and numpy."
        )


def compute_embedding(text: str):
    _ensure_model()
    vec = _model.encode(text, normalize_embeddings=True)
    return vec  # numpy array


def upsert_embedding(file_id: int, text: str):
    """
    Compute embedding for text and upsert into file_embeddings table.
    """
    if not text.strip():
        return  # nothing to embed

    _ensure_model()
    vec = compute_embedding(text)

    embedding_str = json.dumps(vec.tolist())
    now = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO file_embeddings (file_id, embedding, model_name, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(file_id) DO UPDATE SET
            embedding=excluded.embedding,
            model_name=excluded.model_name,
            updated_at=excluded.updated_at
        """,
        (file_id, embedding_str, MODEL_NAME, now, now),
    )

    conn.commit()
    conn.close()


def semantic_search(query: str, top_k: int = 10):
    """
    Brute-force semantic search over all embeddings in SQLite.
    Returns list of {file_id, score}.
    """
    _ensure_model()
    if np is None:
        raise RuntimeError("Numpy not available")

    q_vec = compute_embedding(query)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT file_id, embedding FROM file_embeddings"
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return []

    scores = []
    for file_id, emb_str in rows:
        try:
            vec = np.array(json.loads(emb_str), dtype=float)
            # cosine similarity since both are normalized
            sim = float(np.dot(q_vec, vec))
            scores.append((file_id, sim))
        except Exception:
            continue

    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:top_k]

    return [
        {"file_id": fid, "score": score}
        for fid, score in scores
    ]
