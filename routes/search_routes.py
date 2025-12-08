# routes/search_routes.py

from fastapi import APIRouter, HTTPException, Query
from services.search_service import (
    search_by_content,
    search_by_semantic,
    search_files
)

router = APIRouter(prefix="/search", tags=["search"])


# --------------------------------------------------------
# 1) KEYWORD CONTENT SEARCH
# --------------------------------------------------------
@router.get("/content")
def content_search(q: str = Query(..., description="Keyword to search within extracted document text"),
                   limit: int = 50):
    """
    Full-text keyword search from extracted document content.
    Uses LIKE on file_index table.
    """
    return search_by_content(q, limit)


# --------------------------------------------------------
# 2) SEMANTIC VECTOR SEARCH
# --------------------------------------------------------
@router.get("/semantic")
def semantic_search(q: str = Query(..., description="Natural language query for semantic search"),
                    top_k: int = 10):
    """
    Searches via embeddings (semantic meaning).
    """
    return search_by_semantic(q, top_k)


# --------------------------------------------------------
# 3) METADATA SEARCH
# --------------------------------------------------------
@router.get("/files")
def metadata_search(
    q: str | None = Query(None, description="Substring match on filename"),
    project_id: int | None = Query(None),
    ext: str | None = Query(None, description="File extension without dot (e.g. pdf, xlsx)"),
    tag: str | None = Query(None, description="Tag associated with file"),
    limit: int = 100
):
    """
    Search files by metadata:
    - filename substring
    - project
    - extension
    - tag
    - limits only latest versions
    """
    return search_files(q, project_id, ext, tag, limit)


# --------------------------------------------------------
# 4) COMBINED SEARCH (semantic + content + metadata)
# --------------------------------------------------------
@router.get("/all")
def combined_search(
    q: str = Query(...),
    limit_semantic: int = 5,
    limit_keyword: int = 5,
    limit_meta: int = 20,
):
    """
    Performs combined search across:
        1) semantic embeddings
        2) keyword indexed content
        3) metadata-based filename/tag filters
    
    Returns merged results (deduplicated).
    """

    results = {
        "semantic": [],
        "content": [],
        "metadata": []
    }

    # Semantic search
    try:
        results["semantic"] = search_by_semantic(q, limit_semantic)
    except Exception:
        pass

    # Keyword search
    try:
        results["content"] = search_by_content(q, limit_keyword)
    except Exception:
        pass

    # Metadata search (filename substring)
    try:
        results["metadata"] = search_files(q=q, limit=limit_meta)
    except Exception:
        pass

    # Deduplicate by file_id
    combined_map = {}
    for section in results.values():
        for file in section:
            combined_map[file["id"]] = file

    return {
        "query": q,
        "total": len(combined_map),
        "results": list(combined_map.values()),
        "breakdown": {
            "semantic": len(results["semantic"]),
            "content": len(results["content"]),
            "metadata": len(results["metadata"])
        }
    }
