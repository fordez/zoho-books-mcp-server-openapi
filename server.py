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
# 🔹 Logging DETALLADO
# ====================================================
logging.basicConfig(
    level=logging.DEBUG,  # 🔍 Cambiado a DEBUG para ver TODO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# También activar logs de httpx para ver requests completas
logging.getLogger("httpx").setLevel(logging.DEBUG)


# ====================================================
# 🤖 HERRAMIENTAS ESENCIALES PARA AI AGENT (85 tools)
# ====================================================
ALLOWED_TOOLS = {
    # ============ INVOICES (12 tools) ============
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
    # ============ BILLS (11 tools) ============
    "list_bills",
    "get_bill",
    "create_bill",
    "update_bill",
    "delete_bill",
    "mark_bill_void",
    "mark_bill_open",
    "list_bill_payments",
    "apply_credits_to_bill",
    "get_bill_attachment",
    "add_bill_attachment",
    # ============ CONTACTS (10 tools) ============
    "list_contacts",
    "get_contact",
    "create_contact",
    "update_contact",
    "delete_contact",
    "mark_contact_active",
    "mark_contact_inactive",
    "add_contact_address",
    "update_contact_address",
    "delete_contact_address",
    # ============ ITEMS (8 tools) ============
    "list_items",
    "get_item",
    "create_item",
    "update_item",
    "delete_item",
    "list_item_details",
    "mark_item_active",
    "mark_item_inactive",
    # ============ EXPENSES (8 tools) ============
    "list_expenses",
    "get_expense",
    "create_expense",
    "update_expense",
    "delete_expense",
    "get_expense_receipt",
    "create_expense_receipt",
    "delete_expense_receipt",
    # ============ VENDOR PAYMENTS (6 tools) ============
    "list_vendor_payments",
    "get_vendor_payment",
    "create_vendor_payment",
    "update_vendor_payment",
    "delete_vendor_payment",
    "email_vendor_payment",
    # ============ VENDORS (5 tools) ============
    "list_vendors",
    "get_vendor",
    "create_vendor",
    "update_vendor",
    "delete_vendor",
    # ============ ESTIMATES (7 tools) ============
    "list_estimates",
    "get_estimate",
    "create_estimate",
    "update_estimate",
    "delete_estimate",
    "mark_estimate_accepted",
    "email_estimate",
    # ============ SALES ORDERS (7 tools) ============
    "list_sales_orders",
    "get_sales_order",
    "create_sales_order",
    "update_sales_order",
    "delete_sales_order",
    "mark_sales_order_as_void",
    "email_sales_order",
    # ============ PURCHASE ORDERS (6 tools) ============
    "list_purchase_orders",
    "get_purchase_order",
    "create_purchase_order",
    "update_purchase_order",
    "delete_purchase_order",
    "list_purchase_order_comments",
    # ============ USERS (3 tools) ============
    "list_users",
    "get_user",
    "get_current_user",
    # ============ PROJECTS (2 tools) ============
    "list_projects",
    "get_project",
}


# ====================================================
# 🔧 Zoho API Client Wrapper CON LOGGING COMPLETO
# ====================================================
class ZohoAsyncClient(httpx.AsyncClient):
    """
    Cliente personalizado que transforma requests para Zoho Books API.
    Zoho requiere que POST/PUT envíen datos como form-data con JSONString.
    """

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """
        Intercepta y transforma requests para el formato de Zoho Books.

        GET: Mantiene query params normales
        POST/PUT/PATCH: Convierte JSON body a form-data con JSONString
        """

        logger.info("=" * 80)
        logger.info(f"🔵 INCOMING REQUEST")
        logger.info(f"📍 Method: {method}")
        logger.info(f"🔗 URL: {url}")
        logger.info(f"📦 kwargs keys: {kwargs.keys()}")

        # Log de TODOS los kwargs
        for key, value in kwargs.items():
            if key == "headers":
                logger.info(f"📋 Headers:")
                for h_key, h_val in value.items():
                    logger.info(f"   {h_key}: {h_val}")
            elif key == "params":
                logger.info(f"🔍 Params: {value}")
            elif key == "json":
                logger.info(f"📄 JSON body: {value}")
                logger.info(f"📄 JSON type: {type(value)}")
            elif key == "data":
                logger.info(f"📝 Data body: {value}")
            else:
                logger.info(f"🔧 {key}: {value}")

        # Si hay JSON body en POST/PUT/PATCH, convertir a formato Zoho
        if method.upper() in ["POST", "PUT", "PATCH"]:
            logger.info(f"🔄 Processing {method} request for Zoho format...")

            if "json" in kwargs:
                json_data = kwargs.pop("json")
                logger.info(f"✅ Found JSON data in kwargs")
                logger.info(f"📦 JSON data content: {json_data}")
                logger.info(f"📦 JSON data type: {type(json_data)}")

                # Validar que no sea None o vacío
                if json_data is None:
                    logger.error("❌ JSON data is None!")
                    raise ValueError(f"Cannot {method}: JSON data is None")

                if json_data == {}:
                    logger.warning("⚠️ JSON data is empty dict!")

                # Serializar JSON sin espacios extras
                json_string = json.dumps(json_data, separators=(",", ":"))
                logger.info(f"📝 Serialized JSONString: {json_string}")
                logger.info(f"📝 JSONString length: {len(json_string)}")

                # Convertir a formato form-urlencoded con JSONString
                kwargs["data"] = {"JSONString": json_string}
                logger.info(f"✅ Converted to form-data with JSONString")

                # Cambiar content-type
                if "headers" not in kwargs:
                    kwargs["headers"] = {}
                kwargs["headers"]["Content-Type"] = "application/x-www-form-urlencoded"
                logger.info(f"✅ Set Content-Type to application/x-www-form-urlencoded")
            else:
                logger.warning(f"⚠️ No 'json' key found in kwargs for {method} request")
                logger.info(f"Available kwargs keys: {list(kwargs.keys())}")

        logger.info(f"🚀 Sending request to Zoho API...")
        logger.info("=" * 80)

        # Ejecutar request normal
        response = await super().request(method, url, **kwargs)

        # Log de respuesta COMPLETO
        logger.info("=" * 80)
        logger.info(f"📥 RESPONSE RECEIVED")
        logger.info(f"📊 Status Code: {response.status_code}")
        logger.info(f"📋 Response Headers:")
        for h_key, h_val in response.headers.items():
            logger.info(f"   {h_key}: {h_val}")

        try:
            response_json = response.json()
            logger.info(
                f"📄 Response Body (JSON): {json.dumps(response_json, indent=2)}"
            )
        except:
            logger.info(f"📄 Response Body (Text): {response.text[:500]}")

        logger.info("=" * 80)

        # Log de errores con más detalle
        if response.status_code >= 400:
            logger.error(f"❌ HTTP ERROR {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"❌ Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                logger.error(f"❌ Error Text: {response.text}")

            # Log del request que causó el error
            logger.error(f"❌ Failed request details:")
            logger.error(f"   Method: {method}")
            logger.error(f"   URL: {url}")
            logger.error(f"   Final kwargs: {kwargs}")

        return response


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
# 🔹 Filtrar paths del OpenAPI
# ====================================================
def filter_openapi_paths(spec: dict) -> dict:
    """Filtra los paths del OpenAPI para incluir solo ALLOWED_TOOLS"""
    logger.info("🔍 Starting OpenAPI paths filtering...")

    if not spec or "paths" not in spec:
        logger.warning("⚠️ No paths found in OpenAPI spec")
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
                logger.debug(f"✅ Including: {operation_id} ({method.upper()} {path})")

                # Log detallado del schema para operaciones POST/PUT
                if method.lower() in ["post", "put", "patch"]:
                    request_body = operation.get("requestBody", {})
                    logger.debug(
                        f"   📋 Request body required: {request_body.get('required', False)}"
                    )
                    content = request_body.get("content", {})
                    for content_type, schema_info in content.items():
                        logger.debug(f"   📝 Content-Type: {content_type}")
                        schema = schema_info.get("schema", {})
                        logger.debug(
                            f"   📦 Schema type: {schema.get('type', 'unknown')}"
                        )
                        if "properties" in schema:
                            logger.debug(
                                f"   🔑 Properties: {list(schema['properties'].keys())}"
                            )
                        if "required" in schema:
                            logger.debug(f"   ⚠️  Required fields: {schema['required']}")
            else:
                excluded_count += 1
                logger.debug(f"⏭️  Skipping: {operation_id}")

        if filtered_path_item:
            filtered_paths[path] = filtered_path_item

    logger.info(
        f"✅ Filtering complete: {included_count} included, {excluded_count} excluded"
    )
    spec["paths"] = filtered_paths
    return spec


# ====================================================
# 🔹 Construcción MCP
# ====================================================
def build_mcp() -> FastMCP:
    logger.info("🏗️  Building MCP server...")

    access_token = get_access_token()
    logger.info(f"🔑 Access token (first 20 chars): {access_token[:20]}...")

    # ✅ Usar ZohoAsyncClient personalizado con transformación JSONString
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
    info = {"title": "Zoho Books AI Agent API", "version": "1.0.0"}

    for path in yaml_files:
        try:
            logger.debug(f"📖 Reading: {path}")
            with open(path, "r", encoding="utf-8") as f:
                spec = yaml.safe_load(f)

            if not spec or not spec.get("paths"):
                logger.warning(f"⚠️ El archivo {path} no contiene paths válidos.")
                continue

            paths_count = len(spec.get("paths", {}))
            logger.debug(
                f"   ✅ Loaded {paths_count} paths from {os.path.basename(path)}"
            )

            combined_paths.update(spec.get("paths", {}))
            combined_tags.extend(spec.get("tags", []))

        except Exception as e:
            logger.error(f"❌ Error leyendo {path}: {e}")

    combined_spec = {
        "openapi": "3.0.0",
        "info": info,
        "paths": combined_paths,
        "tags": combined_tags,
    }

    # Filtrar antes de crear MCP
    logger.info(f"📋 Total paths before filtering: {len(combined_spec['paths'])}")
    combined_spec = filter_openapi_paths(combined_spec)
    logger.info(f"✅ Total paths after filtering: {len(combined_spec['paths'])}")
    logger.info(f"🎯 Total allowed tools: {len(ALLOWED_TOOLS)}")

    logger.info("🚀 Building MCP from filtered OpenAPI spec")

    mcp_server = FastMCP.from_openapi(
        openapi_spec=combined_spec,
        client=client,
        route_maps=route_maps,
        name="zoho-mcp-ai-agent",
    )

    logger.info("✅ MCP server built successfully")
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
    os.environ["FASTMCP_HOST"] = "0.0.0.0"
    os.environ["FASTMCP_PORT"] = "8080"

    logger.info("🚀 Starting AI Agent MCP server at http://0.0.0.0:8080/mcp")
    logger.info(f"📊 Registered {len(ALLOWED_TOOLS)} tools")

    try:
        mcp.run(transport="http", host="0.0.0.0", port=8080)
    except Exception as e:
        logger.error(f"❌ Error running MCP server: {e}", exc_info=True)
        if "address already in use" in str(e).lower():
            logger.info(
                "💡 Port 8080 ocupado → liberar con:\n   lsof -ti:8080 | xargs kill -9"
            )
