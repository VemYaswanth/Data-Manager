import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

STORAGE_DIR = BASE_DIR / "storage"
DB_PATH = BASE_DIR / "db" / "vault.db"
LOG_PATH = BASE_DIR / "vault.log"

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 500 * 1024 * 1024))  # default 500MB
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Ensure directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
