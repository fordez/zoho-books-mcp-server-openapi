import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")

# Puertos configurables
OAUTH_PORT = int(os.getenv("OAUTH_PORT", "8081"))
MCP_PORT = int(os.getenv("MCP_PORT", "8080"))

REGION_DISPLAY = {
    "com": "🌍 Global (.com)",
    "in": "🇮🇳 India (.in)",
    "eu": "🇪🇺 Europe (.eu)",
    "com.au": "🇦🇺 Australia (.com.au)",
    "jp": "🇯🇵 Japan (.jp)",
}
