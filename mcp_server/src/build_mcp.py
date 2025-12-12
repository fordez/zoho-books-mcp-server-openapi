import logging
import os

from fastmcp import FastMCP
from fastmcp.experimental.server.openapi import MCPType, RouteMap
from src.openapi_processor import (
    load_openapi_files,
    merge_openapi_specs,
    process_openapi_spec,
)
from src.token_service import get_credentials  # ← Cambiado
from src.zoho_client import ZohoAsyncClient

logger = logging.getLogger(__name__)


def build_mcp() -> FastMCP:
    logger.info("🏗️ Building Zoho MCP server...")

    # Obtener credenciales desde OAuth server
    credentials = get_credentials()

    token = credentials["access_token"]
    api_domain = credentials["api_domain"]
    organization_id = credentials["organization_id"]

    logger.info(f"🏢 Company: {credentials['company_name']}")
    logger.info(f"📧 Email: {credentials['email']}")
    logger.info(f"🌐 Region: {credentials['region']}")

    # Crear cliente con credenciales dinámicas
    client = ZohoAsyncClient(
        base_url=api_domain,  # ← Dinámico desde OAuth
        headers={"Authorization": f"Zoho-oauthtoken {token}"},
        params={"organization_id": organization_id},  # ← Dinámico desde OAuth
        timeout=30.0,
    )

    logger.info(f"🔗 API Domain: {api_domain}")
    logger.info(f"🏢 Org ID: {organization_id}")

    # Cargar OpenAPI specs
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OPENAPI_DIR = os.path.join(BASE_DIR, "openapi-all")

    specs = load_openapi_files(OPENAPI_DIR)
    merged_spec = merge_openapi_specs(specs)
    processed_spec = process_openapi_spec(merged_spec)

    # Crear servidor MCP
    mcp_server = FastMCP.from_openapi(
        openapi_spec=processed_spec,
        client=client,
        route_maps=[
            RouteMap(pattern=r"^/admin/.*", mcp_type=MCPType.EXCLUDE),
            RouteMap(tags={"internal"}, mcp_type=MCPType.EXCLUDE),
        ],
        name="zoho-books-mcp",
    )

    logger.info("✅ MCP server ready")
    return mcp_server
