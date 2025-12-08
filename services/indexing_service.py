# services/indexing_service.py

import sqlite3
from datetime import datetime

from core.config import DB_PATH, STORAGE_DIR
from core.logger import logger

from encryption.crypto_engine import decrypt_bytes
from services.file_service_db import get_file_by_id
from services.text_extraction_service import extract_text_from_bytes
from services.embedding_service import upsert_embedding


def index_file_content(file_id: int):
    """
    Decrypt file → extract text → update file_index → update embedding.
    Safe, idempotent, and robust against binary files.
    """
    file = get_file_by_id(file_id)
    if not file:
        raise ValueError(f"File not found: id={file_id}")

    abs_path = STORAGE_DIR / file["path"]
    if not abs_path.exists():
        raise ValueError(f"File missing on disk: {abs_path}")

    try:
        encrypted = abs_path.read_bytes()
        raw_bytes = decrypt_bytes(encrypted)
    except Exception as e:
        logger.error(f"Decryption failed for file_id={file_id}: {e}")
        return {"indexed": False, "error": "decrypt_failed"}

    # Extract text safely
    text = extract_text_from_bytes(file["name"], raw_bytes) or ""
    if not isinstance(text, str):
        text = str(text)

    now = datetime.utcnow().isoformat()

    # Insert/update file_index
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO file_index (file_id, content, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(file_id) DO UPDATE SET
                content=excluded.content,
                updated_at=excluded.updated_at
            """,
            (file_id, text, now, now),
        )

        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB indexing failed for file_id={file_id}: {e}")
        return {"indexed": False, "error": "db_failed"}

    # Embeddings are optional but logged
    try:
        upsert_embedding(file_id, text)
    except Exception as e:
        logger.error(f"Semantic indexing failed for file_id={file_id}: {e}")

    logger.info(
        f"Indexed content for file_id={file_id} | chars={len(text)} | has_text={bool(text.strip())}"
    )

    return {
        "indexed": True,
        "file_id": file_id,
        "has_text": bool(text.strip()),
        "length": len(text),
    }
