import os
from pathlib import Path

from dotenv import load_dotenv

# Buscar .env un nivel arriba del directorio actual
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    client_id = os.getenv("ZOHO_CLIENT_ID")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET")
    refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
    organization_id = os.getenv("ZOHO_ORG_ID")
    base_url = os.getenv("ZOHO_BASE_URL")


# Debug opcional (puedes quitarlo después)
if not Config.organization_id:
    print(f"⚠️  WARNING: .env not found or ZOHO_ORG_ID missing")
    print(f"📁 Looking for .env at: {env_path}")
else:
    print(f"✅ Loaded organization_id: {Config.organization_id}")
