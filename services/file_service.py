# services/file_service.py

import sqlite3
from datetime import datetime
from fastapi import HTTPException, UploadFile

from core.config import STORAGE_DIR, DB_PATH
from core.logger import logger

from encryption.crypto_engine import encrypt_bytes, decrypt_bytes

from services.validation_service import validate_upload
from services.file_service_db import (
    insert_file_metadata,
    get_file_by_id,
    delete_file_metadata,
    get_all_files,
    get_project_files_latest,
    get_file_versions,
)
from services.project_db import get_project_by_id
from services.project_service import (
    get_project_folder,
    get_version_control_folder,
)
from services.file_version_service import (
    get_next_version,
    get_versioned_filename,
)

from services.audit_service import log_event
from services.indexing_service import index_file_content


# -------------------------------------------------------
# Shared helpers
# -------------------------------------------------------

def _mark_old_versions_not_latest(project_id: int, filename: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE files SET is_latest = 0 WHERE project_id = ? AND name = ?",
        (project_id, filename),
    )
    conn.commit()
    conn.close()


# -------------------------------------------------------
# Upload handler (root)
# -------------------------------------------------------

async def handle_upload(file: UploadFile):
    filename = file.filename
    raw_bytes = await file.read()

    validate_upload(filename, raw_bytes)

    file_path = STORAGE_DIR / filename

    if file_path.exists():
        raise HTTPException(status_code=409, detail="File already exists")

    # Encrypt
    try:
        encrypted_bytes = encrypt_bytes(raw_bytes)
    except Exception:
        raise HTTPException(status_code=500, detail="Encryption failed")

    # Save
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(encrypted_bytes)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save file")

    now = datetime.utcnow().isoformat()
    size = len(encrypted_bytes)

    # Insert metadata
    file_id = insert_file_metadata(
        name=filename,
        path=filename,
        size=size,
        created_at=now,
        modified_at=now,
        project_id=None,
        version=1,
        is_latest=1,
    )

    # INDEXING
    try:
        index_file_content(file_id)
    except Exception as e:
        logger.error(f"Indexing failed for root upload {filename}: {e}")

    log_event("UPLOAD_ROOT", project_id=None, file=filename, version=1)

    return {"message": "File encrypted & uploaded", "version": 1, "file_id": file_id}


# -------------------------------------------------------
# Upload to project (versioned)
# -------------------------------------------------------

async def handle_upload_to_project(project_id: int, file: UploadFile):
    filename = file.filename
    raw_bytes = await file.read()

    validate_upload(filename, raw_bytes)

    # Check project
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_name = project["name"]
    project_folder = get_project_folder(project_name)
    vc_folder = get_version_control_folder(project_name)

    project_folder.mkdir(parents=True, exist_ok=True)
    vc_folder.mkdir(parents=True, exist_ok=True)

    next_version = get_next_version(project_id, filename)

    # Move old version
    existing_path = project_folder / filename
    if existing_path.exists() and next_version > 1:
        prev_version = next_version - 1
        versioned_path = vc_folder / get_versioned_filename(filename, prev_version)
        try:
            versioned_path.parent.mkdir(parents=True, exist_ok=True)
            existing_path.replace(versioned_path)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to move old version")

    # Encrypt
    try:
        encrypted_bytes = encrypt_bytes(raw_bytes)
    except Exception:
        raise HTTPException(status_code=500, detail="Encryption failed")

    # Save new version
    new_file_path = project_folder / filename
    try:
        new_file_path.write_bytes(encrypted_bytes)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save file")

    now = datetime.utcnow().isoformat()
    size = len(encrypted_bytes)

    _mark_old_versions_not_latest(project_id, filename)

    # Insert new version row
    file_id = insert_file_metadata(
        name=filename,
        path=f"{project_name}/{filename}",
        size=size,
        created_at=now,
        modified_at=now,
        project_id=project_id,
        version=next_version,
        is_latest=1,
    )

    # INDEXING
    try:
        index_file_content(file_id)
    except Exception as e:
        logger.error(f"Indexing failed for {filename} (project={project_name}): {e}")

    log_event(
        "UPLOAD_VERSION",
        project_id=project_id,
        file=filename,
        version=next_version,
    )

    return {"message": f"Uploaded version v{next_version}", "version": next_version, "file_id": file_id}


# -------------------------------------------------------
# Download handlers
# -------------------------------------------------------

def handle_download(file_id: int):
    file = get_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    abs_path = STORAGE_DIR / file["path"]

    if not abs_path.exists():
        delete_file_metadata(file_id)
        raise HTTPException(status_code=404, detail="File missing — metadata cleaned")

    encrypted = abs_path.read_bytes()
    decrypted = decrypt_bytes(encrypted)

    log_event("DOWNLOAD", project_id=file.get("project_id"), file=file["name"])

    return file["name"], decrypted


def download_specific_version(file_id: int):
    file = get_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Version not found")

    abs_path = STORAGE_DIR / file["path"]
    if not abs_path.exists():
        raise HTTPException(status_code=404, detail="File missing on disk")

    decrypted = decrypt_bytes(abs_path.read_bytes())

    log_event(
        "DOWNLOAD_VERSION",
        project_id=file.get("project_id"),
        file=file["name"],
        version=file["version"],
    )

    return file["name"], decrypted


# -------------------------------------------------------
# Delete
# -------------------------------------------------------

def handle_delete(file_id: int):
    file = get_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    abs_path = STORAGE_DIR / file["path"]

    if abs_path.exists():
        try:
            abs_path.unlink()
        except:
            raise HTTPException(status_code=500, detail="Failed to delete file")

    delete_file_metadata(file_id)

    log_event(
        "DELETE_FILE",
        project_id=file.get("project_id"),
        file=file["name"],
        version=file.get("version"),
    )

    return {"message": "File deleted"}


# -------------------------------------------------------
# Version history
# -------------------------------------------------------

def list_files_in_project(project_id: int):
    return get_project_files_latest(project_id)


def get_version_history(project_id: int, filename: str):
    versions = get_file_versions(project_id, filename)
    if not versions:
        raise HTTPException(status_code=404, detail="No versions found")
    return versions


def get_version_history_ui(project_id: int, filename: str):
    versions = get_file_versions(project_id, filename)
    if not versions:
        raise HTTPException(status_code=404, detail="No versions found")

    return [
        {
            "file_id": f["id"],
            "version": f["version"],
            "latest": bool(f["is_latest"]),
            "path": f["path"],
            "label": f"{f['name']} (v{f['version']})",
            "modified": f["modified_at"],
        }
        for f in versions
    ]
