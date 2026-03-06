import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

TG_API_ID = int(os.environ["TG_API_ID"])
TG_API_HASH = os.environ["TG_API_HASH"]

SESSION_PATH = str(Path(__file__).parent / "sessions" / "telegram_mcp")
DOWNLOADS_PATH = Path(__file__).parent / "downloads"

# Ensure directories exist
Path(SESSION_PATH).parent.mkdir(parents=True, exist_ok=True)
DOWNLOADS_PATH.mkdir(parents=True, exist_ok=True)
