import glob
import logging
import os
from functools import lru_cache

import httpx
import yaml
from fastmcp import FastMCP
from fastmcp.experimental.server.openapi import MCPType, RouteMap

from config import Config

# ====================================================
# 🔹 Logging básico
# ====================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ====================================================
# 🔹 Función SÍNCRONA para obtener token Zoho
# ====================================================
@lru_cache(maxsize=1)
def get_access_token() -> str:
    """Obtiene el access token de forma síncrona usando httpx.Client"""
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
# 🔹 Construcción MCP SÍNCRONA
# ====================================================
def build_mcp() -> FastMCP:
    """Construye el servidor MCP de forma completamente síncrona"""
    access_token = get_access_token()

    # Cliente síncrono para FastMCP Cloud
    client = httpx.Client(
        base_url=Config.base_url,
        headers={
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json;charset=UTF-8",
            "organization_id": Config.organization_id,
        },
        timeout=30.0,
    )

    route_maps = [
        RouteMap(pattern=r"^/admin/.*", mcp_type=MCPType.EXCLUDE),
        RouteMap(tags={"internal"}, mcp_type=MCPType.EXCLUDE),
        RouteMap(methods=["POST", "PUT", "PATCH", "DELETE"], mcp_type=MCPType.TOOL),
        RouteMap(methods=["GET"], mcp_type=MCPType.RESOURCE),
    ]

    # Cargar specs OpenAPI
    yaml_files = glob.glob("openapi-all/*.yaml") + glob.glob("openapi-all/*.yml")
    combined_paths = {}
    combined_tags = []
    info = {"title": "Zoho Books Combined API", "version": "1.0.0"}

    for path in yaml_files:
        with open(path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        if not spec or not spec.get("paths"):
            continue
        combined_paths.update(spec.get("paths", {}))
        combined_tags.extend(spec.get("tags", []))

    combined_spec = {
        "openapi": "3.0.0",
        "info": info,
        "paths": combined_paths,
        "tags": combined_tags,
        "servers": [{"url": Config.base_url}],
    }

    logger.info("🚀 Building MCP from OpenAPI spec")
    return FastMCP.from_openapi(
        openapi_spec=combined_spec, client=client, route_maps=route_maps
    )


# ====================================================
# 🔹 CRÍTICO: Inicializar mcp durante import
# ====================================================
logger.info("🔄 Initializing MCP server...")
mcp = build_mcp()
logger.info("✅ MCP server initialized successfully")


# ====================================================
# 🔹 Ejecutar MCP localmente (opcional)
# ====================================================
if __name__ == "__main__":
    # Solo para ejecución local
    os.environ["FASTMCP_HOST"] = "0.0.0.0"
    os.environ["FASTMCP_PORT"] = "8080"

    logger.info("🚀 Starting MCP server at http://0.0.0.0:8080")

    try:
        mcp.run(transport="http", host="0.0.0.0", port=8080)
    except Exception as e:
        logger.error(f"❌ Error running MCP server: {e}")
        if "address already in use" in str(e).lower():
            logger.info(
                "💡 Port 8080 is in use. Free it with: lsof -ti:8080 | xargs kill -9"
            )
