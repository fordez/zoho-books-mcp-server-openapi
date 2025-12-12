import sqlite3
from datetime import datetime

from config import MCP_PORT
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from src.auth import (
    generate_auth_url,
    process_oauth_callback,
    refresh_token_if_needed,
)
from src.docs import render_tools_docs_page  # Importa la nueva función
from src.templates import render_home_page
from src.utils import get_base_url, get_ngrok_public_url


def setup_routes(app: FastAPI, db):
    """Configure all application routes"""

    @app.get("/")
    async def home(request: Request):
        """Dashboard showing all connected accounts"""
        conn = db._get_conn()

        # Get all accounts (excluding deleted ones)
        cursor = conn.execute("""
            SELECT * FROM users
            WHERE is_active >= 0
            ORDER BY is_active DESC, last_used DESC, connected_at DESC
        """)
        accounts = [dict(row) for row in cursor.fetchall()]

        # Get active account
        cursor = conn.execute("SELECT * FROM users WHERE is_active = 1")
        row = cursor.fetchone()
        active_account = dict(row) if row else None

        # Construir MCP URL automáticamente
        base_url = get_base_url(request)
        mcp_url = f"{base_url}:{MCP_PORT}/mcp"

        # Si hay un tunnel ngrok activo, usar esa URL en vez de localhost
        ngrok_url = get_ngrok_public_url()
        if ngrok_url:
            mcp_url = f"{ngrok_url}/mcp"

        return HTMLResponse(render_home_page(accounts, active_account, mcp_url))

    @app.get("/tools/docs")  # Nueva ruta para la documentación
    async def tools_docs():
        """Render the MCP Tools Documentation page"""
        return HTMLResponse(render_tools_docs_page())

    @app.post("/account/{user_id}/activate")
    async def activate_account(user_id: str):
        """Set an account as active"""
        conn = db._get_conn()

        # Check if account exists
        cursor = conn.execute(
            "SELECT 1 FROM users WHERE user_id = ? AND is_active >= 0", (user_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(404, "Account not found")

        # Deactivate all accounts first
        conn.execute("UPDATE users SET is_active = 0 WHERE is_active >= 0")

        # Activate selected account
        conn.execute("UPDATE users SET is_active = 1 WHERE user_id = ?", (user_id,))
        conn.commit()

        return {"success": True, "message": "Account activated"}

    @app.delete("/account/{user_id}")
    async def delete_account(user_id: str):
        """Delete an account"""
        conn = db._get_conn()

        cursor = conn.execute(
            "SELECT 1 FROM users WHERE user_id = ? AND is_active >= 0", (user_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(404, "Account not found")

        # Mark as deleted (soft delete with is_active = -1)
        conn.execute("UPDATE users SET is_active = -1 WHERE user_id = ?", (user_id,))
        conn.commit()

        return {"success": True, "message": "Account deleted"}

    @app.get("/oauth/authorize")
    async def authorize():
        """Start OAuth flow - auto-generate user_id"""
        auth_url, user_id = generate_auth_url()
        return RedirectResponse(auth_url)

    @app.get("/oauth/callback")
    async def callback(code: str, state: str, request: Request):
        """OAuth callback handler"""
        user_id = state
        return await process_oauth_callback(code, user_id, request, db)

    @app.get("/token")
    async def get_token():
        """Get token for active account - used by MCP server"""
        conn = db._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM users WHERE is_active = 1")
        row = cursor.fetchone()

        if not row:
            raise HTTPException(
                404, "No active account found. Please select an account."
            )

        account = dict(row)

        # Refresh token if needed
        account = await refresh_token_if_needed(db, account)

        # Update last used
        conn.execute(
            "UPDATE users SET last_used = ? WHERE user_id = ?",
            (datetime.now().isoformat(), account["user_id"]),
        )
        conn.commit()

        return {
            "access_token": account["access_token"],
            "organization_id": account["organization_id"],
            "api_domain": account["api_domain"],
            "region": account["region"],
            "email": account["email"],
            "company_name": account["company_name"],
        }
