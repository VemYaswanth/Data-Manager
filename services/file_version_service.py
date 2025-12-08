# services/file_version_service.py

import os
from core.config import STORAGE_DIR
from services.file_service_db import get_all_files


def get_next_version(project_id: int, filename: str):
    """
    Determines the next version number based on existing files
    in the same project with the same name.
    """
    files = get_all_files()

    matching = [
        f for f in files
        if f["project_id"] == project_id and f["name"] == filename
    ]

    if not matching:
        return 1  # first time this file is uploaded

    return max(f["version"] for f in matching) + 1


def get_versioned_filename(original_name: str, version: int):
    """
    Example: file.pdf → file-v3.pdf
    """
    base, ext = os.path.splitext(original_name)
    return f"{base}-v{version}{ext}"
