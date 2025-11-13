import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    client_id = os.getenv("ZOHO_CLIENT_ID")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET")
    refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
    organization_id = os.getenv("ZOHO_ORG_ID")
    base_url = os.getenv("ZOHO_BASE_URL")
