# services/validation_service.py

import os
from fastapi import HTTPException

MAX_FILE_SIZE_MB = 500  # adjust as needed
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

ILLEGAL_FILENAME_CHARS = set(r'\/:*?"<>|')

def validate_filename(name: str):
    """
    Ensure filenames are safe for the filesystem.
    """
    if name.strip() == "":
        raise HTTPException(status_code=400, detail="Filename cannot be empty")

    if any(c in ILLEGAL_FILENAME_CHARS for c in name):
        raise HTTPException(
            status_code=400,
            detail=f"Filename contains illegal characters: {ILLEGAL_FILENAME_CHARS}"
        )

    if ".." in name:
        raise HTTPException(status_code=400, detail="Invalid filename")

    return True


def validate_file_size(size: int):
    """
    Enforce max file size constraints.
    """
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds the limit of {MAX_FILE_SIZE_MB} MB"
        )
    return True


def validate_upload(filename: str, raw_bytes: bytes):
    """
    Main upload validator used by file_service.py
    """
    validate_filename(filename)
    validate_file_size(len(raw_bytes))
    return True
