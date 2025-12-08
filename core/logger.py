import logging
import os
from core.config import BASE_DIR

LOG_PATH = os.path.join(BASE_DIR, "vault.log")

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("vault")
