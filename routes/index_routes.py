# routes/index_routes.py

from fastapi import APIRouter, HTTPException
from services.indexing_service import index_file_content
from services.file_service_db import get_file_by_id

router = APIRouter(prefix="/index", tags=["indexing"])


@router.post("/file/{file_id}")
def index_single_file(file_id: int):
    """
    Manually trigger indexing of a single file (content + embedding).
    Useful for reindex or backfill.
    """
    file = get_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return index_file_content(file_id)
