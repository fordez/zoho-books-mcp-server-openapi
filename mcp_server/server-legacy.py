import os

os.environ["FASTMCP_HOST"] = "0.0.0.0"
os.environ["FASTMCP_PORT"] = "8080"

import glob
import logging
import time
from threading import Lock

import httpx
import yaml
from config import Config
from fastmcp import FastMCP
from fastmcp.experimental.server.openapi import MCPType, RouteMap
from src.constants import ALLOWED_TOOLS
from src.openapi_utils import (
    add_missing_request_schemas,
    filter_openapi_paths,
    fix_missing_parameters,
    fix_parameter_schemas,
    remove_all_refs_from_schemas,
)
from src.zoho_client import ZohoAsyncClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.INFO)

_token_cache = {"token": None, "expires_at": 0}
_token_lock = Lock()


# =====================================================================
# TOKEN HANDLING
# =====================================================================


def get_access_token() -> str:
    with _token_lock:
        now = time.time()

        if _token_cache["token"] and now < (_token_cache["expires_at"] - 300):
            logger.debug("Using cached token")
            return _token_cache["token"]

        logger.info("🔐 Refreshing token...")

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
                raise Exception(f"No token returned: {res}")

            expires_in = res.get("expires_in", 3600)

            _token_cache["token"] = res["access_token"]
            _token_cache["expires_at"] = now + expires_in

            logger.info(f"Token refreshed (expires in {expires_in}s)")
            return _token_cache["token"]


# =====================================================================
# REMOVE RESPONSE SCHEMAS
# =====================================================================


def remove_response_schemas(spec):
    """Elimina todos los schemas de respuesta para evitar validación"""
    logger.info("🔥 Removing response schemas...")

    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue

            if "responses" in operation:
                for status_code, response_def in operation["responses"].items():
                    if "content" in response_def:
                        response_def.pop("content")

    logger.info("Response schemas removed")
    return spec


# =====================================================================
# BUILD MCP SERVER
# =====================================================================


def build_mcp() -> FastMCP:
    logger.info("🏗️ Building MCP server...")

    access_token = get_access_token()
    logger.info(f"🔑 Token: {access_token[:20]}...")

    client = ZohoAsyncClient(
        base_url=Config.base_url,
        headers={"Authorization": f"Zoho-oauthtoken {access_token}"},
        params={"organization_id": Config.organization_id},
        timeout=30.0,
    )

    logger.info(f"🔗 Base URL: {Config.base_url}")
    logger.info(f"🏢 Organization: {Config.organization_id}")

    # ----------------------------------------------------------------
    # OPENAPI FILES DIRECTORY (NOW INSIDE THE MCP SERVER)
    # ----------------------------------------------------------------

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OPENAPI_DIR = os.path.join(BASE_DIR, "openapi-all")

    logger.info(f"📁 Using OpenAPI directory: {OPENAPI_DIR}")

    yaml_files = sorted(
        glob.glob(os.path.join(OPENAPI_DIR, "*.yaml"))
        + glob.glob(os.path.join(OPENAPI_DIR, "*.yml")),
        key=lambda x: (
            0
            if "invoices" in x.lower()
            else 1
            if "customer-debit-notes" in x.lower()
            else 2
        ),
    )

    logger.info(f"📄 Found {len(yaml_files)} YAML files")

    # Combined spec
    combined_paths = {}
    combined_tags = []
    combined_schemas = {}
    combined_parameters = {}

    info = {"title": "Zoho Books AI Agent API", "version": "1.0.0"}

    # ----------------------------------------------------------------
    # MERGE YAML FILES
    # ----------------------------------------------------------------
    for path in yaml_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                spec = yaml.safe_load(f)

            if not spec:
                continue

            # Paths
            if "paths" in spec:
                for spec_path, path_item in spec["paths"].items():
                    if spec_path not in combined_paths:
                        combined_paths[spec_path] = path_item
                    else:
                        # Merge HTTP methods
                        for key, value in path_item.items():
                            if key in combined_paths[spec_path] and key.lower() in [
                                "get",
                                "post",
                                "put",
                                "patch",
                                "delete",
                            ]:
                                continue
                            combined_paths[spec_path][key] = value

            # Tags
            if "tags" in spec:
                combined_tags.extend(spec["tags"])

            # Schemas + parameters
            if "components" in spec:
                combined_schemas.update(spec["components"].get("schemas", {}))
                combined_parameters.update(spec["components"].get("parameters", {}))

        except Exception as e:
            logger.error(f"Error loading {path}: {e}")

    # Final merged spec
    combined_spec = {
        "openapi": "3.0.0",
        "info": info,
        "paths": combined_paths,
        "tags": combined_tags,
        "components": {
            "schemas": combined_schemas,
            "parameters": combined_parameters,
        },
    }

    logger.info(f"📋 Paths: {len(combined_spec['paths'])}")
    logger.info(f"📦 Schemas: {len(combined_schemas)}")

    # ----------------------------------------------------------------
    # PROCESSING PIPELINE
    # ----------------------------------------------------------------

    combined_spec = fix_missing_parameters(combined_spec)
    combined_spec = add_missing_request_schemas(combined_spec)
    combined_spec = remove_all_refs_from_schemas(combined_spec)
    combined_spec = fix_parameter_schemas(combined_spec)
    combined_spec = filter_openapi_paths(combined_spec, ALLOWED_TOOLS)
    combined_spec = remove_response_schemas(combined_spec)

    logger.info(f"Filtered paths: {len(combined_spec['paths'])}")

    # ----------------------------------------------------------------
    # BUILD MCP
    # ----------------------------------------------------------------

    mcp_server = FastMCP.from_openapi(
        openapi_spec=combined_spec,
        client=client,
        route_maps=[
            RouteMap(pattern=r"^/admin/.*", mcp_type=MCPType.EXCLUDE),
            RouteMap(tags={"internal"}, mcp_type=MCPType.EXCLUDE),
        ],
        name="zoho-mcp-ai-agent",
    )

    logger.info("MCP server ready")
    return mcp_server


# =====================================================================
# RUN SERVER
# =====================================================================

try:
    logger.info("Initializing MCP server...")
    mcp = build_mcp()
    logger.info("Initialized OK")
except Exception as e:
    logger.error(f"❌ Error: {e}", exc_info=True)
    raise e


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("🚀 Starting MCP at http://0.0.0.0:8080/mcp")
    logger.info("📊 Tools loaded: %s", len(ALLOWED_TOOLS))
    logger.info("⚠️ Response validation disabled")
    logger.info("=" * 80)

    try:
        mcp.run(transport="http", host="0.0.0.0", port=8080)
    except Exception as e:
        logger.error(f"❌ Error running MCP: {e}", exc_info=True)
