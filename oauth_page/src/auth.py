import secrets
import traceback
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import httpx
from config import (
    MCP_PORT,
    ZOHO_CLIENT_ID,
    ZOHO_CLIENT_SECRET,
    ZOHO_REDIRECT_URI,
)
from fastapi import Request
from fastapi.responses import HTMLResponse
from src.templates import (
    render_error_page,
    render_setup_required_page,
    render_success_page,
)
from src.utils import extract_region_from_domain, get_base_url


async def exchange_code_for_tokens(code: str) -> Dict:
    """Exchange authorization code for access tokens"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://accounts.zoho.com/oauth/v2/token",
            data={
                "grant_type": "authorization_code",
                "client_id": ZOHO_CLIENT_ID,
                "client_secret": ZOHO_CLIENT_SECRET,
                "redirect_uri": ZOHO_REDIRECT_URI,
                "code": code,
            },
        )

        if resp.status_code != 200:
            error_data = (
                resp.json()
                if resp.headers.get("content-type") == "application/json"
                else resp.text
            )
            raise Exception(f"Token exchange failed: {error_data}")

        tokens = resp.json()

        # Check if we got an error in the token response
        if "error" in tokens:
            raise Exception(f"Zoho OAuth error: {tokens.get('error')}")

        return tokens


async def get_organization_data(api_domain: str, access_token: str) -> Optional[Dict]:
    """Get organization data from Zoho Books API"""
    async with httpx.AsyncClient() as client:
        org_resp = await client.get(
            f"{api_domain}/books/v3/organizations",
            headers={"Authorization": f"Zoho-oauthtoken {access_token}"},
        )

        if org_resp.status_code != 200:
            error_data = (
                org_resp.json()
                if org_resp.headers.get("content-type") == "application/json"
                else org_resp.text
            )
            raise Exception(
                f"Failed to get organization (status {org_resp.status_code}): {error_data}"
            )

        org_response = org_resp.json()

        # Check if we have organizations
        if "organizations" not in org_response or not org_response["organizations"]:
            return None

        return org_response["organizations"][0]


def check_duplicate_organization(
    db, organization_id: str
) -> Tuple[bool, Optional[str]]:
    """
    Check if organization already exists.
    Returns: (is_duplicate, company_name)
    """
    conn = db._get_conn()
    cursor = conn.execute(
        "SELECT user_id, company_name FROM users WHERE organization_id = ? AND is_active >= 0",
        (organization_id,),
    )
    existing = cursor.fetchone()

    if existing:
        return True, existing[1]
    return False, None


def save_and_activate_account(db, user_id: str, account_data: Dict) -> None:
    """Save account and set as active"""
    # Save account
    db.save_user(user_id, account_data)

    # Ensure only ONE account is active
    conn = db._get_conn()
    # First, deactivate all accounts
    conn.execute("UPDATE users SET is_active = 0 WHERE is_active >= 0")
    # Then activate the new account
    conn.execute("UPDATE users SET is_active = 1 WHERE user_id = ?", (user_id,))
    conn.commit()


async def process_oauth_callback(
    code: str, user_id: str, request: Request, db
) -> HTMLResponse:
    """
    Main OAuth callback processing logic.
    Returns HTML response with success or error page.
    """
    try:
        # Step 1: Exchange code for tokens
        tokens = await exchange_code_for_tokens(code)

        # Step 2: Extract region
        api_domain = tokens.get("api_domain", "https://www.zohoapis.com")
        region = extract_region_from_domain(api_domain)
        print(f"🌍 Detected region: {region} from {api_domain}")

        # Step 3: Get organization data
        org_data = await get_organization_data(api_domain, tokens["access_token"])

        # Step 4: Check if organization exists (new account without setup)
        if not org_data:
            print(f"ℹ️ New account without organization - Region: {region}")
            return HTMLResponse(render_setup_required_page(region))

        organization_id = org_data["organization_id"]

        # Step 5: Check for duplicates
        is_duplicate, existing_company = check_duplicate_organization(
            db, organization_id
        )
        if is_duplicate:
            error_msg = (
                f"⚠️ This Zoho Books account is already connected.\n\n"
                f"Company: {existing_company}\n"
                f"Organization ID: {organization_id}\n\n"
                f"Please delete the existing account first if you want to reconnect it."
            )
            print(f"⚠️ Duplicate account attempt: {organization_id}")
            return HTMLResponse(render_error_page(error_msg), status_code=400)

        # Step 6: Save account
        account_data = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": (
                datetime.now() + timedelta(seconds=tokens["expires_in"])
            ).isoformat(),
            "organization_id": organization_id,
            "api_domain": api_domain,
            "region": region,
            "connected_at": datetime.now().isoformat(),
            "email": org_data.get("email", ""),
            "company_name": org_data.get("name", ""),
        }

        save_and_activate_account(db, user_id, account_data)
        print(f"✅ Account connected: {org_data.get('name')} ({organization_id})")

        # Step 7: Build MCP URL and return success page
        base_url = get_base_url(request)
        mcp_url = f"{base_url}:{MCP_PORT}/mcp"

        return HTMLResponse(render_success_page(org_data, region, mcp_url))

    except Exception as e:
        error_msg = str(e)
        error_details = traceback.format_exc()
        print(f"❌ OAuth Error: {error_msg}\n{error_details}")
        return HTMLResponse(render_error_page(error_msg), status_code=500)


def generate_auth_url() -> Tuple[str, str]:
    """
    Generate OAuth authorization URL and user_id.
    Returns: (auth_url, user_id)
    """
    user_id = f"account_{secrets.token_hex(6)}"

    auth_url = (
        f"https://accounts.zoho.com/oauth/v2/auth"
        f"?scope=ZohoBooks.fullaccess.all"
        f"&client_id={ZOHO_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={ZOHO_REDIRECT_URI}"
        f"&access_type=offline"
        f"&prompt=consent"
        f"&state={user_id}"
    )

    return auth_url, user_id


async def refresh_token_if_needed(db, account: Dict) -> Dict:
    """
    Refresh access token if it's about to expire.
    Returns updated account dict.
    """
    expires_at = datetime.fromisoformat(account["expires_at"])

    # Refresh if token expires in less than 5 minutes
    if datetime.now() + timedelta(minutes=5) >= expires_at:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://accounts.zoho.com/oauth/v2/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": ZOHO_CLIENT_ID,
                    "client_secret": ZOHO_CLIENT_SECRET,
                    "refresh_token": account["refresh_token"],
                },
            )
            if resp.status_code == 200:
                new_tokens = resp.json()
                new_expires = (
                    datetime.now() + timedelta(seconds=new_tokens["expires_in"])
                ).isoformat()
                db.update_tokens(
                    account["user_id"], new_tokens["access_token"], new_expires
                )
                account["access_token"] = new_tokens["access_token"]
            else:
                print(f"⚠️ Token refresh failed: {resp.status_code} - {resp.text}")

    return account
