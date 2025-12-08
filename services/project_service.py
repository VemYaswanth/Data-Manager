import os
import shutil
from fastapi import HTTPException

from core.config import STORAGE_DIR
from core.logger import logger

from services.project_db import (
    create_project,
    get_project_by_id,
    get_all_projects,
    delete_project_from_db
)

# ---------- PROJECT NAME VALIDATION ----------
ILLEGAL_CHARS = set(r'\/:*?"<>|')

def validate_project_name(name: str):
    if name.strip() == "":
        raise HTTPException(status_code=400, detail="Project name cannot be empty")

    if any(c in ILLEGAL_CHARS for c in name):
        raise HTTPException(
            status_code=400,
            detail=f"Project name contains illegal characters: {ILLEGAL_CHARS}"
        )

    if ".." in name:
        raise HTTPException(status_code=400, detail="Invalid project name")


# ---------- PATH HELPERS ----------
def ensure_project_folder(name: str):
    """
    Ensure the project folder and Version Control subfolder exist.
    """
    project_path = STORAGE_DIR / name
    vc_path = project_path / "Version Control"

    project_path.mkdir(parents=True, exist_ok=True)
    vc_path.mkdir(parents=True, exist_ok=True)

    return project_path


def get_project_folder(project_name: str):
    return STORAGE_DIR / project_name


def get_version_control_folder(project_name: str):
    return STORAGE_DIR / project_name / "Version Control"


# ---------- CREATE ----------
def handle_project_create(name: str):
    name = name.strip()
    validate_project_name(name)

    # Check duplicate
    exists = [p for p in get_all_projects() if p["name"].lower() == name.lower()]
    if exists:
        raise HTTPException(status_code=409, detail="Project already exists")

    project_id = create_project(name)
    ensure_project_folder(name)

    logger.info(f"Project created: {name} (id={project_id})")
    return {"id": project_id, "name": name}


# ---------- LIST ----------
def handle_project_list():
    return get_all_projects()


# ---------- GET ----------
def handle_project_get(project_id: int):
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ---------- DELETE ----------
def handle_project_delete(project_id: int):
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_path = STORAGE_DIR / project["name"]
    vc_path = project_path / "Version Control"

    # Check if project folder contains anything other than Version Control
    if any(
        item for item in project_path.iterdir()
        if item.name != "Version Control"
    ):
        raise HTTPException(
            status_code=400,
            detail="Project contains files—delete them first."
        )

    # Check if Version Control is empty
    if vc_path.exists() and any(vc_path.iterdir()):
        raise HTTPException(
            status_code=400,
            detail="Version Control contains files—clear them first."
        )

    delete_project_from_db(project_id)

    # Remove entire folder tree safely
    if os.path.exists(project_path):
        shutil.rmtree(project_path)

    logger.info(f"Project deleted: {project['name']} (id={project_id})")
    return {"message": "Project deleted"}
