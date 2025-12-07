from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

import os
from datetime import datetime

from core.logger import logger
from core.db_init import init_db
from core.config import STORAGE_DIR

from file_system.folder_scanner import scan_and_index
from services.file_service import (
    get_all_files,
    insert_file_metadata,
    get_file_by_id,
    delete_file_metadata,
)

from encryption.crypto_engine import encrypt_bytes, decrypt_bytes
from services.consistency_service import check_consistency

# ============================================================
# INIT
# ============================================================
app = FastAPI(title="Vault Backend")
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")

ALLOWED_MAX_SIZE = 500 * 1024 * 1024  # 500 MB max size


# ============================================================
# STARTUP
# ============================================================
@app.on_event("startup")
def startup_event():
    init_db()


# ============================================================
# HEALTH
# ============================================================
@app.get("/")
def root():
    return {"status": "Vault backend is running"}


# ============================================================
# CONSISTENCY CHECK + REPAIR
# ============================================================
@app.get("/consistency")
def consistency_check():
    missing = check_consistency()
    logger.info(f"Consistency check found {len(missing)} missing files")
    return {"missing_files": missing}


@app.post("/repair")
def repair():
    missing = check_consistency()
    for fid in missing:
        delete_file_metadata(fid)

    logger.info(f"Repaired DB – removed {len(missing)} missing entries")
    return {"fixed": len(missing)}


# ============================================================
# SCAN
# ============================================================
@app.post("/scan")
def scan_files():
    scan_and_index()
    return {"message": "Scan complete"}


# ============================================================
# LIST FILES
# ============================================================
@app.get("/files")
def list_files():
    return get_all_files()


# ============================================================
# UPLOAD + ENCRYPT
# ============================================================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.filename.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid filename")

    raw_bytes = await file.read()

    # Size limit
    if len(raw_bytes) > ALLOWED_MAX_SIZE:
        logger.error(f"Upload failed – file too large: {file.filename}")
        raise HTTPException(status_code=400, detail="File too large")

    file_path = os.path.join(STORAGE_DIR, file.filename)

    # Prevent overwriting (for your future version-control system)
    if os.path.exists(file_path):
        logger.error(f"Upload blocked – file exists: {file.filename}")
        raise HTTPException(status_code=409, detail="File already exists")

    encrypted_bytes = encrypt_bytes(raw_bytes)

    # Save encrypted
    with open(file_path, "wb") as f:
        f.write(encrypted_bytes)

    now = datetime.utcnow().isoformat()
    insert_file_metadata(
        name=file.filename,
        path=file.filename,
        size=len(encrypted_bytes),
        created_at=now,
        modified_at=now,
    )

    logger.info(f"Encrypted + uploaded: {file.filename}")
    return {"message": "File encrypted & uploaded"}


# ============================================================
# DOWNLOAD + DECRYPT
# ============================================================
@app.get("/download/{file_id}")
def download_file(file_id: int):
    file = get_file_by_id(file_id)
    if not file:
        logger.error(f"Download failed – metadata missing for id {file_id}")
        raise HTTPException(status_code=404, detail="File not found")

    abs_path = os.path.join(STORAGE_DIR, file["path"])

    if not os.path.exists(abs_path):
        logger.error(f"Encrypted file missing on disk: {abs_path}")
        delete_file_metadata(file_id)
        raise HTTPException(status_code=404, detail="File missing – metadata cleaned")

    with open(abs_path, "rb") as f:
        encrypted = f.read()

    try:
        decrypted = decrypt_bytes(encrypted)
    except Exception as e:
        logger.error(f"Decryption failed for {file['name']}: {str(e)}")
        raise HTTPException(status_code=500, detail="Decryption failed")

    logger.info(f"Decrypted + downloaded: {file['name']}")

    return StreamingResponse(
        iter([decrypted]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file["name"]}"'}
    )


# ============================================================
# DELETE
# ============================================================
@app.delete("/files/{file_id}")
def delete_file(file_id: int):
    file = get_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    abs_path = os.path.join(STORAGE_DIR, file["path"])

    if os.path.exists(abs_path):
        os.remove(abs_path)

    delete_file_metadata(file_id)
    return {"message": "File deleted"}
