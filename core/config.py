import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STORAGE_DIR = os.path.join(BASE_DIR, "storage")
DB_PATH = os.path.join(BASE_DIR, "db", "vault.db")

# Create storage folder if missing
os.makedirs(STORAGE_DIR, exist_ok=True)
