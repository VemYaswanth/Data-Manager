# services/ai_service.py

from services.search_service import (
    search_by_semantic,
    search_by_content,
    search_files,
)
from services.text_extraction_service import extract_text_from_bytes
from services.file_service_db import get_file_by_id
from encryption.crypto_engine import decrypt_bytes
from core.config import STORAGE_DIR
from core.logger import logger

# OPTIONAL – GPT4All or local LLaMA backend
try:
    from gpt4all import GPT4All

    llm = GPT4All("Meta-Llama-3-8B.Q4_0.gguf")  # replace with your local model
except Exception as e:
    llm = None
    logger.error(f"Local LLM not loaded: {e}")


def _load_file_content(file_record: dict) -> str:
    """
    Loads + decrypts + extracts text from a file.
    file_record is a row dict returned by get_file_by_id / search_*.
    """
    abs_path = STORAGE_DIR / file_record["path"]
    encrypted = abs_path.read_bytes()
    raw = decrypt_bytes(encrypted)
    return extract_text_from_bytes(file_record["name"], raw)


def _get_candidates(
    question: str,
    k_docs: int,
    project_id: int | None,
    tag: str | None,
    ext: str | None,
):
    """
    Decide which files to consider for answering this question.
    - If any filter is present → rely on metadata search with filters
    - Else → combine semantic + keyword + metadata
    Returns a list of unique file dicts.
    """
    file_map: dict[int, dict] = {}

    # If user applied filters, we respect those STRICTLY
    if project_id is not None or tag is not None or ext is not None:
        try:
            hits = search_files(
                q=question,
                project_id=project_id,
                ext=ext,
                tag=tag,
                limit=k_docs,
            )
        except Exception as e:
            logger.error(f"Filtered metadata search failed: {e}")
            hits = []

        for f in hits:
            file_map[f["id"]] = f

    else:
        # Global (unfiltered) mode: combine semantic + content + metadata
        try:
            semantic_hits = search_by_semantic(question, top_k=k_docs)
        except Exception:
            semantic_hits = []

        try:
            keyword_hits = search_by_content(question, limit=k_docs)
        except Exception:
            keyword_hits = []

        try:
            meta_hits = search_files(q=question, limit=k_docs)
        except Exception:
            meta_hits = []

        for group in (semantic_hits, keyword_hits, meta_hits):
            for f in group:
                # search_by_semantic/search_by_content already return file dicts
                file_map[f["id"]] = f

    return list(file_map.values())[:k_docs]


def ai_query_engine(
    question: str,
    k_docs: int = 5,
    project_id: int | None = None,
    tag: str | None = None,
    ext: str | None = None,
):
    """
    Main AI engine (backwards compatible):
      - Accepts optional filters: project_id, tag, ext
      - Picks candidate files
      - Decrypts + extracts content
      - Calls local LLM
    """

    if not question or question.strip() == "":
        return {"error": "Empty question"}

    # 1) Choose candidate files
    candidates = _get_candidates(question, k_docs, project_id, tag, ext)

    if not candidates:
        return {"answer": "No relevant files found.", "sources": []}

    # 2) Extract text from retrieved documents
    docs = []
    for f in candidates:
        try:
            text = _load_file_content(f)
            if text.strip():
                docs.append({"file": f, "text": text})
        except Exception as e:
            logger.error(f"Failed to load content for file {f['id']}: {e}")

    if not docs:
        return {
            "answer": "Files were found, but their content could not be read or extracted.",
            "sources": [c["name"] for c in candidates],
        }

    # 3) Build prompt
    context = "\n\n".join(
        f"[File: {d['file']['name']}]\n{d['text'][:5000]}" for d in docs
    )

    prompt = f"""
You are a local AI assistant accessing a secure private file vault.

Answer the following question using ONLY the context from the files provided below.
If you don't know the answer from the files, say exactly:
"The documents do not contain enough information."

QUESTION:
{question}

CONTEXT:
{context}

Provide:
1) A clear, concise answer.
2) Bullet-point reasoning if useful.
3) Which files you used.
"""

    if llm:
        try:
            answer = llm.generate(prompt, max_tokens=300)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            answer = "Local LLM call failed. Check model / configuration."
    else:
        answer = "Local LLM not configured. Install GPT4All or another local backend."

    return {
        "question": question,
        "answer": answer,
        "sources": [d["file"]["name"] for d in docs],
    }


# Convenience wrapper for routes
def ask_ai(
    question: str,
    project_id: int | None = None,
    tag: str | None = None,
    ext: str | None = None,
    k_docs: int = 5,
):
    """
    Thin wrapper used by /ai/ask route.
    """
    return ai_query_engine(
        question=question,
        k_docs=k_docs,
        project_id=project_id,
        tag=tag,
        ext=ext,
    )
