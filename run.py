import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage" / "projects"

def ensure_folders():
    """Create required folders if they do not exist."""
    print("Ensuring project directories exist...")
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

def load_env():
    """Load .env file and validate keys."""
    print("Loading environment variables...")
    load_dotenv()

    master_key = os.getenv("MASTER_KEY")
    if not master_key:
        print("ERROR: MASTER_KEY missing from .env file.")
        exit(1)

    print("Environment OK.")
    return master_key

def start_streamlit():
    """Launch Streamlit dashboard."""
    print("Starting Streamlit dashboard...")
    cmd = [
        "streamlit",
        "run",
        str(BASE_DIR / "frontend" / "dashboard.py"),
        "--server.port=8501",
        "--server.headless=true"
    ]
    subprocess.Popen(cmd)

def main():
    print("\n🔐 Secure File Vault Starting...\n")
    
    ensure_folders()
    load_env()
    start_streamlit()
    
    print("\nSystem is running at: http://localhost:8501\n")
    print("Press Ctrl+C to stop.")

if __name__ == "__main__":
    main()
