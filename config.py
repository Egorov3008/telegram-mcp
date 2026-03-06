import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

TG_API_ID = int(os.environ["TG_API_ID"])
TG_API_HASH = os.environ["TG_API_HASH"]

SESSION_PATH = str(Path(__file__).parent / "sessions" / "telegram_mcp")

# Ensure sessions directory exists
Path(SESSION_PATH).parent.mkdir(parents=True, exist_ok=True)
