# routes/project_routes.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from services.project_service import (
    handle_project_create,
    handle_project_list,
    handle_project_get,
    handle_project_delete,
)
from services.file_service import (
    handle_upload_to_project,
    list_files_in_project,
    get_version_history,
    get_version_history_ui,
    download_specific_version,
)

router = APIRouter(prefix="/projects", tags=["projects"])


# -------------------------------------------------------
# Create Project
# -------------------------------------------------------

@router.post("/", operation_id="project_create")
def create_project(name: str):
    return handle_project_create(name)


# -------------------------------------------------------
# List Projects
# -------------------------------------------------------

@router.get("/", operation_id="project_list")
def list_projects():
    return handle_project_list()


# -------------------------------------------------------
# Get Single Project
# -------------------------------------------------------

@router.get("/{project_id}", operation_id="project_get")
def get_project(project_id: int):
    return handle_project_get(project_id)


# -------------------------------------------------------
# Delete Project
# -------------------------------------------------------

@router.delete("/{project_id}", operation_id="project_delete")
def delete_project(project_id: int):
    return handle_project_delete(project_id)


# -------------------------------------------------------
# Upload File Into Project (VERSIONED UPLOAD)
# -------------------------------------------------------

@router.post("/{project_id}/upload", operation_id="project_upload_file")
async def upload_into_project(project_id: int, file: UploadFile = File(...)):
    return await handle_upload_to_project(project_id, file)


# -------------------------------------------------------
# List Latest Files in Project
# -------------------------------------------------------

@router.get("/{project_id}/files", operation_id="project_file_list")
def list_project_files(project_id: int):
    return list_files_in_project(project_id)


# -------------------------------------------------------
# Raw Version History
# -------------------------------------------------------

@router.get("/{project_id}/files/{filename}/versions", operation_id="project_version_history")
def version_history(project_id: int, filename: str):
    return get_version_history(project_id, filename)


# -------------------------------------------------------
# UI-Friendly Version History
# -------------------------------------------------------

@router.get("/{project_id}/files/{filename}/versions-ui", operation_id="project_version_history_ui")
def version_history_ui(project_id: int, filename: str):
    return get_version_history_ui(project_id, filename)


# -------------------------------------------------------
# Download Specific Version
# -------------------------------------------------------

@router.get("/{project_id}/files/version/{file_id}/download", operation_id="project_version_download")
def download_version(project_id: int, file_id: int):
    filename, content = download_specific_version(file_id)
    return {
        "filename": filename,
        "content": content,
    }
