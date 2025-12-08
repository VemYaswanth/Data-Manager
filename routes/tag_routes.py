from fastapi import APIRouter
from services.tag_service import add_tag, remove_tag, list_tags_for_file

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/file/{file_id}")
def add_tag_to_file(file_id: int, tag: str):
    return add_tag(file_id, tag)


@router.delete("/file/{file_id}")
def delete_tag_from_file(file_id: int, tag: str):
    return remove_tag(file_id, tag)


@router.get("/file/{file_id}")
def get_tags_for_file(file_id: int):
    return list_tags_for_file(file_id)
