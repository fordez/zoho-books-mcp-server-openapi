import glob
import logging
import os
from functools import lru_cache

import httpx
import yaml
from fastmcp import FastMCP
from fastmcp.experimental.server.openapi import MCPType, RouteMap

from config import Config
from src.constants import ALLOWED_TOOLS
from src.openapi_utils import (
    add_missing_request_schemas, 
    filter_openapi_paths,
    remove_all_refs_from_schemas,
    fix_parameter_schemas  # 🔥 NUEVA FUNCIÓN
)
from src.zoho_client import ZohoAsyncClient

# ====================================================
# 🔹 Logging DETALLADO
# ====================================================
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# También activar logs de httpx para ver requests completas
logging.getLogger("httpx").setLevel(logging.DEBUG)


# ====================================================
# 🔹 Obtener token Zoho
# ====================================================
@lru_cache(maxsize=1)
def get_access_token() -> str:
    """Obtiene el token solo durante la inicialización (síncrono)"""
    logger.info("🔐 Requesting Zoho access token...")
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
            logger.error(f"❌ No access token in response: {res}")
            raise Exception(f"No access token obtained: {res}")
        logger.info("✅ Access token obtained successfully")
        return res["access_token"]


# ====================================================
# 🔹 Construcción MCP
# ====================================================
def build_mcp() -> FastMCP:
    logger.info("🏗️  Building MCP server...")

    access_token = get_access_token()
    logger.info(f"🔑 Access token (first 20 chars): {access_token[:20]}...")

    # 🔥 Cliente personalizado que SIMPLIFICA respuestas automáticamente
    client = ZohoAsyncClient(
        base_url=Config.base_url,
        headers={
            "Authorization": f"Zoho-oauthtoken {access_token}",
        },
        params={
            "organization_id": Config.organization_id,
        },
        timeout=30.0,
    )
    logger.info(f"🔗 Base URL: {Config.base_url}")
    logger.info(f"🏢 Organization ID: {Config.organization_id}")

    route_maps = [
        RouteMap(pattern=r"^/admin/.*", mcp_type=MCPType.EXCLUDE),
        RouteMap(tags={"internal"}, mcp_type=MCPType.EXCLUDE),
    ]

    # ====================================================
    # 🔹 Combinar OpenAPI
    # ====================================================
    logger.info("📂 Loading OpenAPI YAML files...")
    yaml_files = glob.glob("openapi-all/*.yaml") + glob.glob("openapi-all/*.yml")
    logger.info(f"📄 Found {len(yaml_files)} YAML files")

    combined_paths = {}
    combined_tags = []
    combined_schemas = {}
    info = {"title": "Zoho Books AI Agent API", "version": "1.0.0"}

    for path in yaml_files:
        try:
            logger.debug(f"📖 Reading: {path}")
            with open(path, "r", encoding="utf-8") as f:
                spec = yaml.safe_load(f)

            if not spec:
                continue

            # Combinar paths
            if "paths" in spec:
                paths_count = len(spec["paths"])
                logger.debug(
                    f"   ✅ Loaded {paths_count} paths from {os.path.basename(path)}"
                )
                combined_paths.update(spec["paths"])

            # Combinar tags
            if "tags" in spec:
                combined_tags.extend(spec["tags"])

            # Combinar schemas
            if "components" in spec and "schemas" in spec["components"]:
                schemas_count = len(spec["components"]["schemas"])
                logger.debug(f"   📦 Loaded {schemas_count} schemas")
                combined_schemas.update(spec["components"]["schemas"])

        except Exception as e:
            logger.error(f"❌ Error leyendo {path}: {e}")

    combined_spec = {
        "openapi": "3.0.0",
        "info": info,
        "paths": combined_paths,
        "tags": combined_tags,
        "components": {"schemas": combined_schemas},
    }

    logger.info(f"📋 Total paths: {len(combined_spec['paths'])}")
    logger.info(f"📦 Total schemas loaded: {len(combined_schemas)}")

    # 🔥 ORDEN CORRECTO DE TRANSFORMACIONES:
    # 1. Primero agregar schemas faltantes (analiza TODOS los paths)
    combined_spec = add_missing_request_schemas(combined_spec)

    # 2. Limpiar todas las referencias $ref rotas
    combined_spec = remove_all_refs_from_schemas(combined_spec)

    # 3. 🔥 NUEVO: Arreglar esquemas de parámetros (page, per_page, etc)
    combined_spec = fix_parameter_schemas(combined_spec)

    # 4. Luego filtrar paths (solo incluye ALLOWED_TOOLS)
    combined_spec = filter_openapi_paths(combined_spec, ALLOWED_TOOLS)

    logger.info(f"✅ Total paths after filtering: {len(combined_spec['paths'])}")
    logger.info(f"🎯 Total allowed tools: {len(ALLOWED_TOOLS)}")

    logger.info("🚀 Building MCP from filtered OpenAPI spec")
    logger.info("✂️ ZohoAsyncClient will simplify complex responses automatically")
    logger.info("🔧 All $ref in response schemas have been removed")
    logger.info("🔧 All parameter schemas have been fixed")

    mcp_server = FastMCP.from_openapi(
        openapi_spec=combined_spec,
        client=client,
        route_maps=route_maps,
        name="zoho-mcp-ai-agent",
    )

    logger.info("✅ MCP server built successfully")
    logger.info("🛡️  Protection against validation errors: ACTIVE")
    return mcp_server


# ====================================================
# 🔹 Inicializar MCP
# ====================================================
try:
    logger.info("🔄 Initializing AI Agent MCP server...")
    mcp = build_mcp()
    logger.info("✅ MCP server initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing MCP server: {e}", exc_info=True)
    raise e


# ====================================================
# 🔹 Ejecutar MCP
# ====================================================
if __name__ == "__main__":
    os.environ["FASTMCP_EXPERIMENTAL_ENABLE_NEW_OPENAPI_PARSER"] = "true"
    os.environ["FASTMCP_HOST"] = "0.0.0.0"
    os.environ["FASTMCP_PORT"] = "8080"

    logger.info("=" * 80)
    logger.info("🚀 Starting AI Agent MCP server at http://0.0.0.0:8080/mcp")
    logger.info(f"📊 Registered {len(ALLOWED_TOOLS)} tools")
    logger.info("🆕 Using NEW OpenAPI parser")
    logger.info("🛡️  Schema error protection:")
    logger.info("   ✅ Response simplification enabled (ZohoAsyncClient)")
    logger.info("   ✅ $ref removal enabled (openapi_utils)")
    logger.info("   ✅ Parameter schema fixing enabled (openapi_utils)")
    logger.info("=" * 80)

    try:
        mcp.run(transport="http", host="0.0.0.0", port=8080)
    except Exception as e:
        logger.error(f"❌ Error running MCP server: {e}", exc_info=True)
        if "address already in use" in str(e).lower():
            logger.info(
                "💡 Port 8080 ocupado → liberar con:\n   lsof -ti:8080 | xargs kill -9"
            )
