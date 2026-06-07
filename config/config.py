import os
from dotenv import load_dotenv

load_dotenv()

VK_TOKEN: str = os.getenv("VK_TOKEN", "")
VK_GROUP_ID: int = int(os.getenv("VK_GROUP_ID", "0"))
VK_ADMIN_ID: int = int(os.getenv("VK_ADMIN_ID", "0"))

AVITO_CLIENT_ID: str = os.getenv("AVITO_CLIENT_ID", "")
AVITO_CLIENT_SECRET: str = os.getenv("AVITO_CLIENT_SECRET", "")
AVITO_USER_ID: int = int(os.getenv("AVITO_USER_ID", "0"))
AVITO_POLL_INTERVAL: int = int(os.getenv("AVITO_POLL_INTERVAL", "30"))

if not VK_TOKEN:
    raise RuntimeError("VK_TOKEN не задан в .env")
if not VK_GROUP_ID:
    raise RuntimeError("VK_GROUP_ID не задан в .env")
if not VK_ADMIN_ID:
    raise RuntimeError("VK_ADMIN_ID не задан в .env")
if not AVITO_CLIENT_ID:
    raise RuntimeError("AVITO_CLIENT_ID не задан в .env")
if not AVITO_CLIENT_SECRET:
    raise RuntimeError("AVITO_CLIENT_SECRET не задан в .env")
if not AVITO_USER_ID:
    raise RuntimeError("AVITO_USER_ID не задан в .env")
