from fastapi import FastAPI
from core.db_init import init_db
from file_system.folder_scanner import scan_and_index
from services.file_service import get_all_files

app = FastAPI(title="Vault Backend")

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {"status": "Vault backend is running"}

@app.post("/scan")
def scan_files():
    scan_and_index()
    return {"message": "Scan complete"}

@app.get("/files")
def list_files():
    return get_all_files()
