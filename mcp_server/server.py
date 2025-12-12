import logging
import os

os.environ["FASTMCP_HOST"] = "0.0.0.0"
os.environ["FASTMCP_PORT"] = "8080"

from fastmcp import FastMCP
from fastmcp.experimental.server.openapi import MCPType, RouteMap
from src.openapi_loader import load_and_process_openapi
from src.token_service import get_credentials  # ← Cambiado
from src.zoho_client import ZohoAsyncClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.INFO)


def build_mcp() -> FastMCP:
    logger.info("🏗️ Building MCP server...")

    # Obtener todas las credenciales desde OAuth server
    credentials = get_credentials()

    access_token = credentials["access_token"]
    organization_id = credentials["organization_id"]
    api_domain = credentials["api_domain"]

    logger.info(f"🔑 Token: {access_token[:20]}...")
    logger.info(f"🏢 Company: {credentials['company_name']}")
    logger.info(f"📧 Email: {credentials['email']}")
    logger.info(f"🌐 Region: {credentials['region']}")

    # Crear cliente con credenciales dinámicas
    client = ZohoAsyncClient(
        base_url=api_domain,  # ← Dinámico desde OAuth
        headers={"Authorization": f"Zoho-oauthtoken {access_token}"},
        params={"organization_id": organization_id},  # ← Dinámico desde OAuth
        timeout=30.0,
    )

    logger.info(f"🔗 API Domain: {api_domain}")
    logger.info(f"🏢 Org ID: {organization_id}")

    # Cargar y procesar OpenAPI specs
    combined_spec = load_and_process_openapi()

    # Crear servidor MCP
    mcp_server = FastMCP.from_openapi(
        openapi_spec=combined_spec,
        client=client,
        route_maps=[
            RouteMap(pattern=r"^/admin/.*", mcp_type=MCPType.EXCLUDE),
            RouteMap(tags={"internal"}, mcp_type=MCPType.EXCLUDE),
        ],
        name="zoho-books-mcp",
    )

    logger.info("✅ MCP server ready")
    return mcp_server


# RUN
if __name__ == "__main__":
    try:
        logger.info("=" * 80)
        logger.info("🚀 Zoho Books MCP Server")
        logger.info("=" * 80)
        logger.info("Initializing MCP server...")

        mcp = build_mcp()

        logger.info("=" * 80)
        logger.info("✅ Server ready at http://0.0.0.0:8080/mcp")
        logger.info("🔄 Auto-refresh from OAuth server enabled")
        logger.info("=" * 80)

        mcp.run(transport="http", host="0.0.0.0", port=8080)

    except Exception as e:
        logger.error(f"❌ Error running MCP: {e}", exc_info=True)
        raise e
