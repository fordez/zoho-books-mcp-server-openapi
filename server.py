import glob
import json
import logging
import os
from functools import lru_cache
from typing import Any

import httpx
import yaml
from fastmcp import FastMCP
from fastmcp.experimental.server.openapi import MCPType, RouteMap

from config import Config

# ====================================================
# 🔹 Basic logging
# ====================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ====================================================
# 🤖 ALLOWED TOOLS (85 tools)
# ====================================================
ALLOWED_TOOLS = {
    "list_invoices",
    "get_invoice",
    "create_invoice",
    "update_invoice",
    "delete_invoice",
    "email_invoice",
    "mark_invoice_sent",
    "mark_invoice_void",
    "list_invoice_payments",
    "apply_credits_to_invoice",
    "get_invoice_attachment",
    "add_invoice_attachment",
    # ... (all your other tools unchanged)
}


# ====================================================
# 🔧 Zoho API Async Client
# ====================================================
class ZohoAsyncClient(httpx.AsyncClient):
    """
    Custom HTTP client that transforms requests for Zoho Books API.
    Zoho requires POST/PUT requests to send form-data with JSONString.
    """

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        if method.upper() in ["POST", "PUT", "PATCH"] and "json" in kwargs:
            json_data = kwargs.pop("json")
            json_string = json.dumps(json_data, separators=(",", ":"))

            logger.info(f"🔄 {method} {url}")
            logger.info(f"📦 Original data: {json_data}")
            logger.info(f"📝 JSONString: {json_string}")

            kwargs["data"] = {"JSONString": json_string}
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            kwargs["headers"]["Content-Type"] = "application/x-www-form-urlencoded"

        response = await super().request(method, url, **kwargs)

        if response.status_code >= 400:
            try:
                error_data = response.json()
                logger.error(f"❌ API Error: {error_data}")
            except:
                logger.error(f"❌ API Error: {response.text}")
        return response


# ====================================================
# 🔹 Get Zoho access token
# ====================================================
@lru_cache(maxsize=1)
def get_access_token() -> str:
    """Get Zoho access token (sync, cached)"""
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": Config.refresh_token,
        "client_id": Config.client_id,
        "client_secret": Config.client_secret,
        "grant_type": "refresh_token",
    }

    with httpx.Client() as client:
        resp = client.post(token_url, data=data)
        resp.raise_for_status()
        res = resp.json()
        if "access_token" not in res:
            raise Exception(f"No access token obtained: {res}")
        logger.info("🔐 Access token obtained")
        return res["access_token"]


# ====================================================
# 🔹 Filter OpenAPI paths
# ====================================================
def filter_openapi_paths(spec: dict) -> dict:
    """Filter OpenAPI paths to include only ALLOWED_TOOLS"""
    if not spec or "paths" not in spec:
        return spec

    filtered_paths = {}
    included_count = 0
    excluded_count = 0

    for path, path_item in spec.get("paths", {}).items():
        filtered_path_item = {}
        for method, operation in path_item.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue
            operation_id = operation.get("operationId")
            if operation_id in ALLOWED_TOOLS:
                filtered_path_item[method] = operation
                included_count += 1
                logger.info(f"✅ Including: {operation_id}")
            else:
                excluded_count += 1
                logger.debug(f"⏭️  Skipping: {operation_id}")
        if filtered_path_item:
            filtered_paths[path] = filtered_path_item

    logger.info(
        f"📊 Filtering complete: {included_count} included, {excluded_count} excluded"
    )
    spec["paths"] = filtered_paths
    return spec


# ====================================================
# 🔹 Build MCP
# ====================================================
def build_mcp() -> FastMCP:
    access_token = get_access_token()

    client = ZohoAsyncClient(
        base_url=Config.base_url,
        headers={"Authorization": f"Zoho-oauthtoken {access_token}"},
        params={"organization_id": Config.organization_id},
        timeout=30.0,
    )

    route_maps = [
        RouteMap(pattern=r"^/admin/.*", mcp_type=MCPType.EXCLUDE),
        RouteMap(tags={"internal"}, mcp_type=MCPType.EXCLUDE),
    ]

    # Load and merge OpenAPI YAML files
    yaml_files = glob.glob("openapi-all/*.yaml") + glob.glob("openapi-all/*.yml")
    combined_paths = {}
    combined_tags = []
    info = {"title": "Zoho Books AI Agent API", "version": "1.0.0"}

    for path in yaml_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                spec = yaml.safe_load(f)
            if not spec or not spec.get("paths"):
                logger.warning(f"⚠️ File {path} has no valid paths")
                continue
            combined_paths.update(spec.get("paths", {}))
            combined_tags.extend(spec.get("tags", []))
        except Exception as e:
            logger.error(f"❌ Error reading {path}: {e}")

    combined_spec = {
        "openapi": "3.0.0",
        "info": info,
        "paths": combined_paths,
        "tags": combined_tags,
    }

    combined_spec = filter_openapi_paths(combined_spec)
    logger.info(f"✅ Total paths after filtering: {len(combined_spec['paths'])}")
    logger.info(f"🎯 Total allowed tools: {len(ALLOWED_TOOLS)}")

    return FastMCP.from_openapi(
        openapi_spec=combined_spec,
        client=client,
        route_maps=route_maps,
        name="zoho-mcp-ai-agent",
    )


# ====================================================
# 🔹 Initialize MCP
# ====================================================
try:
    logger.info("🔄 Initializing AI Agent MCP server...")
    mcp = build_mcp()
    logger.info("✅ MCP server initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing MCP server: {e}")
    raise e

# ====================================================
# 🔹 Run MCP
# ====================================================
if __name__ == "__main__":
    os.environ["FASTMCP_HOST"] = "0.0.0.0"
    os.environ["FASTMCP_PORT"] = "8080"

    logger.info("🚀 Starting AI Agent MCP server at http://0.0.0.0:8080/mcp")

    try:
        mcp.run(transport="http", host="0.0.0.0", port=8080)
    except Exception as e:
        logger.error(f"❌ Error running MCP server: {e}")
        if "address already in use" in str(e).lower():
            logger.info(
                "💡 Port 8080 is busy → free it with:\n   lsof -ti:8080 | xargs kill -9"
            )
