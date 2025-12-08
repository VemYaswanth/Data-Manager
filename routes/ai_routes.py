from fastapi import APIRouter, HTTPException
from services.search_service import search_files
from services.semantic_rerank_service import build_answer
from services.memory_service import add_message, get_memory

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/ask")
def ask_ai(
    q: str,
    session_id: str,
    project_id: int = None,
    tag: str = None,
    ext: str = None
):
    from services.memory_service import add_message, get_memory

    if not q or q.strip() == "":
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Store user message
    add_message(session_id, "user", q)

    # Retrieve memory context
    context = get_memory(session_id)

    # Search relevant files
    search_results = search_files(
        q=q,
        project_id=project_id,
        tag=tag,
        ext=ext,
        limit=20
    )

    # Generate AI answer
    answer, sources = build_answer(q, context, search_results)

    # Store assistant reply
    add_message(session_id, "assistant", answer)

    return {
        "answer": answer,
        "sources": sources,
        "session_id": session_id,
        "memory_preview": context
    }

from services.memory_service import (
    reset_memory,
    reset_all_memory,
    pin_message
)


@router.post("/reset")
def reset(session_id: str):
    reset_memory(session_id)
    return {"message": "Conversation memory cleared", "session": session_id}


@router.post("/reset_all")
def reset_all(session_id: str):
    reset_all_memory(session_id)
    return {"message": "All memory cleared", "session": session_id}


@router.post("/pin")
def pin(session_id: str, content: str):
    pin_message(session_id, content)
    return {"message": "Pinned to memory", "session": session_id}
