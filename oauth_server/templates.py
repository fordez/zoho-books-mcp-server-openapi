from typing import Dict, List, Optional

from config import REGION_DISPLAY


def get_base_style() -> str:
    """Dark theme CSS - GitHub inspired"""
    return """
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background: #0d1117;
                color: #c9d1d9;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                color: #58a6ff;
                margin-bottom: 10px;
                font-size: 32px;
            }
            h2 {
                color: #58a6ff;
                margin: 20px 0 15px 0;
                font-size: 24px;
            }
            .header {
                background: #161b22;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 20px;
                border: 1px solid #30363d;
            }
            .card {
                background: #161b22;
                padding: 20px;
                border-radius: 12px;
                margin: 15px 0;
                border: 1px solid #30363d;
            }
            .account-card {
                background: #161b22;
                padding: 20px;
                margin: 15px 0;
                border-radius: 12px;
                border: 1px solid #30363d;
                transition: all 0.3s ease;
            }
            .account-card:hover {
                border-color: #58a6ff;
                box-shadow: 0 0 20px rgba(88, 166, 255, 0.1);
                transform: translateY(-2px);
            }
            .account-card.active {
                background: linear-gradient(135deg, #1f6feb 0%, #8957e5 100%);
                border: 2px solid #58a6ff;
                box-shadow: 0 0 30px rgba(88, 166, 255, 0.3);
            }
            .badge {
                background: #238636;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                display: inline-block;
                margin-left: 10px;
            }
            .btn {
                background: #238636;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                text-decoration: none;
                display: inline-block;
                transition: all 0.2s;
                font-weight: 500;
            }
            .btn:hover {
                background: #2ea043;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(46, 160, 67, 0.4);
            }
            .btn-primary {
                background: #1f6feb;
            }
            .btn-primary:hover {
                background: #388bfd;
                box-shadow: 0 4px 12px rgba(56, 139, 253, 0.4);
            }
            .btn-danger {
                background: #da3633;
            }
            .btn-danger:hover {
                background: #f85149;
                box-shadow: 0 4px 12px rgba(248, 81, 73, 0.4);
            }
            .btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none !important;
            }
            .alert {
                padding: 15px 20px;
                border-radius: 8px;
                margin: 15px 0;
                border-left: 4px solid;
            }
            .alert-success {
                background: rgba(35, 134, 54, 0.15);
                border-color: #238636;
                color: #7ee787;
            }
            .alert-warning {
                background: rgba(210, 153, 34, 0.15);
                border-color: #d29922;
                color: #f0c768;
            }
            .alert-info {
                background: rgba(56, 139, 253, 0.15);
                border-color: #388bfd;
                color: #58a6ff;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin: 15px 0;
            }
            .info-item {
                background: rgba(88, 166, 255, 0.1);
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #30363d;
            }
            .info-item strong {
                color: #58a6ff;
                display: block;
                margin-bottom: 5px;
                font-size: 12px;
            }
            code {
                background: #0d1117;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                border: 1px solid #30363d;
                color: #f0883e;
            }
            .mcp-url-box {
                background: #161b22;
                padding: 20px;
                border-radius: 8px;
                border: 2px solid #238636;
                margin: 20px 0;
            }
            .mcp-url-box h3 {
                color: #7ee787;
                margin-bottom: 10px;
                font-size: 16px;
            }
            .mcp-url-box code {
                display: block;
                word-break: break-all;
                margin: 10px 0;
                font-size: 12px;
                padding: 12px;
            }
            .actions {
                display: flex;
                gap: 10px;
                flex-direction: column;
            }
            .steps {
                background: rgba(88, 166, 255, 0.05);
                padding: 20px;
                border-radius: 8px;
                margin: 15px 0;
                border: 1px solid #30363d;
            }
            .steps ol {
                margin-left: 20px;
                color: #c9d1d9;
            }
            .steps li {
                margin: 10px 0;
                line-height: 1.6;
            }
            a { color: #58a6ff; text-decoration: none; }
            a:hover { text-decoration: underline; }

            @media (max-width: 768px) {
                .grid { grid-template-columns: 1fr; }
            }
        </style>
    """


def render_setup_required_page(region: str) -> str:
    """Render setup required page for new Zoho accounts without organization"""

    # Determine the correct Zoho Books URL based on region
    zoho_books_urls = {
        "com": "https://books.zoho.com",
        "in": "https://books.zoho.in",
        "eu": "https://books.zoho.eu",
        "com.au": "https://books.zoho.com.au",
        "jp": "https://books.zoho.jp",
    }

    books_url = zoho_books_urls.get(region, "https://books.zoho.com")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Setup Required</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {get_base_style()}
    </head>
    <body>
        <div class="container" style="max-width: 800px; margin-top: 60px;">
            <div class="card" style="text-align: center;">
                <h1 style="color: #f0c768; margin-bottom: 20px;">📋 Organization Setup Required</h1>

                <div class="alert alert-info" style="text-align: left; margin: 20px 0;">
                    <strong>✨ Welcome to Zoho Books!</strong><br>
                    Your Zoho account was successfully authenticated, but you need to complete the setup by creating your first organization (Organization ID).
                </div>

                <div style="text-align: left; margin: 30px 0;">
                    <h2 style="font-size: 20px; margin-bottom: 15px;">🚀 Quick Setup Guide</h2>

                    <div class="steps">
                        <ol>
                            <li>
                                <strong>Go to Zoho Books:</strong> Click the button below to open Zoho Books
                            </li>
                            <li>
                                <strong>Create Organization:</strong> Follow the setup wizard to create your company/organization
                            </li>
                            <li>
                                <strong>Complete Basic Info:</strong> Enter your company name, address, and fiscal year
                            </li>
                            <li>
                                <strong>Return Here:</strong> Once done, come back and reconnect your account
                            </li>
                        </ol>
                    </div>

                    <div style="background: rgba(88, 166, 255, 0.1); padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #58a6ff;">
                        <strong style="color: #58a6ff;">💡 Tip:</strong>
                        <span style="color: #8b949e; font-size: 14px;">
                            The setup wizard takes about 2-3 minutes. You'll need your company details and preferred currency.
                        </span>
                    </div>
                </div>

                <div style="margin: 30px 0; display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                    <a href="{books_url}" target="_blank" class="btn btn-primary" style="font-size: 16px; padding: 12px 30px;">
                        🌐 Open Zoho Books Setup
                    </a>
                    <a href="/" class="btn" style="font-size: 16px; padding: 12px 30px;">
                        ← Back to Dashboard
                    </a>
                </div>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #30363d;">
                    <p style="color: #8b949e; font-size: 13px;">
                        <strong>Region:</strong> {region.upper()} •
                        <strong>URL:</strong> <code style="font-size: 11px;">{books_url}</code>
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


def render_home_page(
    accounts: List[Dict], active_account: Optional[Dict], mcp_url: str
) -> str:
    """Render main dashboard page"""

    # Active account alert with MCP URL
    if active_account:
        active_info = f"""
        <div class="alert alert-success">
            <strong>✅ Active Account:</strong> {active_account.get("company_name", "N/A")}
            ({active_account.get("region", "com").upper()})
            <br><small>This account will be used by your MCP server</small>
        </div>

        <div class="mcp-url-box">
            <h3>🔗 MCP Server URL</h3>
            <p style="color: #8b949e; font-size: 13px; margin-bottom: 10px;">
                Use this URL to connect your MCP server
            </p>
            <code>{mcp_url}</code>
            <button onclick="copyUrl('{mcp_url}')" class="btn btn-primary" style="margin-top: 10px; font-size: 12px;">
                📋 Copy URL
            </button>
        </div>
        """
    else:
        active_info = """
        <div class="alert alert-warning">
            <strong>⚠️ No Active Account</strong>
            <br><small>Please select an account to use with the MCP server</small>
        </div>
        """

    # Accounts list
    accounts_html = ""
    for acc in accounts:
        is_active = acc.get("is_active", 0) == 1
        last_used = acc.get("last_used", "")[:19] if acc.get("last_used") else "Never"
        connected_at = (
            acc.get("connected_at", "")[:19] if acc.get("connected_at") else "Unknown"
        )
        region_display = REGION_DISPLAY.get(
            acc.get("region", "com"), f"🌐 {acc.get('region', 'com')}"
        )

        active_badge = '<span class="badge">✓ ACTIVE</span>' if is_active else ""
        card_class = "account-card active" if is_active else "account-card"

        action_btn = ""
        if is_active:
            action_btn = '<button class="btn" disabled>✓ Active</button>'
        else:
            action_btn = f'<button class="btn btn-primary" onclick="setActive(\'{acc["user_id"]}\')">Set Active</button>'

        accounts_html += f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="margin-bottom: 15px;">
                        <strong style="font-size: 20px;">🏢 {acc.get("company_name", "N/A")}</strong>
                        {active_badge}
                    </div>
                    <div class="grid">
                        <div class="info-item">
                            <strong>📧 Email</strong>
                            {acc.get("email", "N/A")}
                        </div>
                        <div class="info-item">
                            <strong>🌐 Region</strong>
                            {region_display}
                        </div>
                        <div class="info-item">
                            <strong>🏷️ Organization ID</strong>
                            <code>{acc.get("organization_id", "")[:25]}...</code>
                        </div>
                        <div class="info-item">
                            <strong>⏰ Last Used</strong>
                            {last_used}
                        </div>
                    </div>
                </div>
                <div class="actions" style="margin-left: 20px;">
                    {action_btn}
                    <button class="btn btn-danger" onclick="deleteAccount('{acc["user_id"]}', '{acc.get("company_name", acc["user_id"])}')">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        </div>
        """

    if not accounts_html:
        accounts_html = '<p style="color: #8b949e; text-align: center; padding: 40px;">No accounts connected yet</p>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Zoho Books Accounts</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {get_base_style()}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Zoho Books Account Manager</h1>
                <p style="color: #8b949e;">Manage multiple Zoho Books accounts and select which one to use</p>
            </div>

            {active_info}

            <div class="card">
                <h2>📋 Connected Accounts ({len(accounts)})</h2>
                {accounts_html}
            </div>

            <div class="card" style="text-align: center;">
                <h2>➕ Connect New Account</h2>
                <p style="color: #8b949e; margin: 10px 0;">Add another Zoho Books account</p>
                <a href="/oauth/authorize" class="btn btn-primary" style="margin-top: 10px;">
                    🚀 Connect Zoho Books
                </a>
            </div>
        </div>

        <script>
            function setActive(userId) {{
                if (confirm('Set this account as active?')) {{
                    fetch('/account/' + encodeURIComponent(userId) + '/activate', {{ method: 'POST' }})
                        .then(r => r.json())
                        .then(() => location.reload())
                        .catch(e => alert('Error: ' + e));
                }}
            }}

            function deleteAccount(userId, companyName) {{
                if (confirm('Delete account "' + companyName + '"? This cannot be undone.')) {{
                    fetch('/account/' + encodeURIComponent(userId), {{ method: 'DELETE' }})
                        .then(r => r.json())
                        .then(() => {{
                            alert('✅ Account deleted successfully');
                            location.reload();
                        }})
                        .catch(e => alert('❌ Error: ' + e));
                }}
            }}

            function copyUrl(url) {{
                navigator.clipboard.writeText(url).then(() => {{
                    alert('✅ URL copied to clipboard!');
                }}).catch(() => {{
                    const el = document.createElement('textarea');
                    el.value = url;
                    document.body.appendChild(el);
                    el.select();
                    document.execCommand('copy');
                    document.body.removeChild(el);
                    alert('✅ URL copied to clipboard!');
                }});
            }}
        </script>
    </body>
    </html>
    """


def render_success_page(org_data: Dict, region: str, mcp_url: str) -> str:
    """Render OAuth success page"""
    region_display = {
        "com": "Global",
        "in": "India",
        "eu": "Europe",
        "com.au": "Australia",
        "jp": "Japan",
    }.get(region, region)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Account Connected</title>
        <meta charset="UTF-8">
        {get_base_style()}
    </head>
    <body>
        <div class="container" style="max-width: 700px; margin-top: 80px;">
            <div class="card" style="text-align: center;">
                <h1 style="color: #7ee787; margin-bottom: 20px;">✅ Account Connected Successfully</h1>

                <div style="background: rgba(88, 166, 255, 0.1); padding: 20px; border-radius: 8px; margin: 20px 0; text-align: left;">
                    <div style="margin: 10px 0;">
                        <strong style="color: #58a6ff;">🏢 Company:</strong> {org_data.get("name")}
                    </div>
                    <div style="margin: 10px 0;">
                        <strong style="color: #58a6ff;">📧 Email:</strong> {org_data.get("email")}
                    </div>
                    <div style="margin: 10px 0;">
                        <strong style="color: #58a6ff;">🌐 Region:</strong> {region_display} (.{region})
                    </div>
                    <div style="margin: 10px 0;">
                        <strong style="color: #58a6ff;">🏷️ Organization ID:</strong><br>
                        <code style="font-size: 11px;">{org_data["organization_id"]}</code>
                    </div>
                </div>

                <div class="mcp-url-box">
                    <h3>🔗 MCP Server URL</h3>
                    <p style="color: #8b949e; font-size: 13px; margin-bottom: 10px;">
                        Use this URL to connect your MCP server
                    </p>
                    <code>{mcp_url}</code>
                    <button onclick="copyUrl('{mcp_url}')" class="btn btn-primary" style="margin-top: 10px;">
                        📋 Copy URL
                    </button>
                </div>

                <a href="/" class="btn btn-primary" style="margin-top: 20px;">
                    ← Back to Dashboard
                </a>
            </div>
        </div>

        <script>
            function copyUrl(url) {{
                navigator.clipboard.writeText(url).then(() => {{
                    alert('✅ URL copied to clipboard!');
                }}).catch(() => {{
                    const el = document.createElement('textarea');
                    el.value = url;
                    document.body.appendChild(el);
                    el.select();
                    document.execCommand('copy');
                    document.body.removeChild(el);
                    alert('✅ URL copied to clipboard!');
                }});
            }}
        </script>
    </body>
    </html>
    """


def render_error_page(error: str) -> str:
    """Render error page"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error</title>
        <meta charset="UTF-8">
        {get_base_style()}
    </head>
    <body>
        <div class="container" style="max-width: 600px; margin-top: 100px;">
            <div class="card" style="text-align: center;">
                <h1 style="color: #f85149; margin-bottom: 20px;">❌ Error</h1>
                <div style="background: rgba(248, 81, 73, 0.15); padding: 20px; border-radius: 8px; border-left: 4px solid #f85149; margin: 20px 0;">
                    <p style="color: #f85149; font-family: monospace; font-size: 14px; text-align: left; word-break: break-word;">{error}</p>
                </div>
                <a href="/" class="btn btn-primary">← Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    """
