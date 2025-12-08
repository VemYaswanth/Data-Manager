# main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from core.db_init import init_db
from core.logger import logger

from routes.analytics_routes import router as analytics_router

from routes.tag_routes import router as tag_router
from routes.search_routes import router as search_router
from routes.index_routes import router as index_router
from routes.search_routes import router as search_router
from routes.ai_routes import router as ai_router

# File services
from services.file_service import (
    handle_upload,
    handle_download,
    handle_delete,
)
from services.file_service_db import get_all_files

# Consistency tools
from services.consistency_service import check_consistency, auto_repair

# Project router (projects + versioning)
from routes.project_routes import router as project_router
from routes.search_routes import router as search_router


# -------------------------------------------------------
# App Initialization
# -------------------------------------------------------

app = FastAPI(title="Vault Backend")


# -------------------------------------------------------
# CORS (required for Phase 4 UI)
# -------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # eventually replace with tailscale domain patterns
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# Routers
# -------------------------------------------------------

app.include_router(project_router)
app.include_router(analytics_router)
app.include_router(project_router)
app.include_router(tag_router)
app.include_router(search_router)
app.include_router(index_router)
app.include_router(search_router)
app.include_router(ai_router)


# -------------------------------------------------------
# Static UI (Frontend)
# -------------------------------------------------------

app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")


# -------------------------------------------------------
# Startup
# -------------------------------------------------------

@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Vault backend initialized.")


# -------------------------------------------------------
# System Endpoints
# -------------------------------------------------------

@app.get("/")
def health():
    return {"status": "running"}


# -------------------------------------------------------
# Upload / Download / Delete (root-level)
# -------------------------------------------------------

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return await handle_upload(file)


@app.get("/download/{file_id}")
def download_file(file_id: int):
    filename, decrypted_bytes = handle_download(file_id)

    return StreamingResponse(
        iter([decrypted_bytes]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.delete("/files/{file_id}")
def delete_file(file_id: int):
    return handle_delete(file_id)


@app.get("/files")
def list_files():
    return get_all_files()


# -------------------------------------------------------
# Integrity + Repair Endpoints
# -------------------------------------------------------

@app.get("/consistency")
def consistency_check():
    missing = check_consistency()
    return {"missing_files": missing}


@app.post("/repair")
def repair_db_only():
    """Remove DB entries for missing files. Does NOT touch disk."""
    missing = check_consistency()
    from services.file_service_db import delete_file_metadata

    for fid in missing:
        delete_file_metadata(fid)

    return {"fixed": len(missing)}


@app.post("/repair/full")
def repair_full():
    """Full repair: orphan cleanup + DB fix."""
    return auto_repair()
