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
# 🔹 Logging básico
# ====================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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
# 🔧 Zoho API Client Wrapper
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

        # Si hay JSON body en POST/PUT/PATCH, convertir a formato Zoho
        if method.upper() in ["POST", "PUT", "PATCH"] and "json" in kwargs:
            json_data = kwargs.pop("json")

            # Serializar JSON sin espacios extras
            json_string = json.dumps(json_data, separators=(",", ":"))

            logger.info(f"🔄 {method} {url}")
            logger.info(f"📦 Original data: {json_data}")
            logger.info(f"📝 JSONString: {json_string}")

            # Convertir a formato form-urlencoded con JSONString
            kwargs["data"] = {"JSONString": json_string}

            # Cambiar content-type
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            kwargs["headers"]["Content-Type"] = "application/x-www-form-urlencoded"

        # Ejecutar request normal
        response = await super().request(method, url, **kwargs)

        # Log de respuesta para debugging
        if response.status_code >= 400:
            try:
                error_data = response.json()
                logger.error(f"❌ API Error: {error_data}")
            except:
                logger.error(f"❌ API Error: {response.text}")

        return response


# ====================================================
# 🔹 Obtener token Zoho
# ====================================================
@lru_cache(maxsize=1)
def get_access_token() -> str:
    """Obtiene el token solo durante la inicialización (síncrono)"""
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
# 🔹 Filtrar paths del OpenAPI
# ====================================================
def filter_openapi_paths(spec: dict) -> dict:
    """Filtra los paths del OpenAPI para incluir solo ALLOWED_TOOLS"""
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
# 🔹 Construcción MCP
# ====================================================
def build_mcp() -> FastMCP:
    access_token = get_access_token()

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

    route_maps = [
        RouteMap(pattern=r"^/admin/.*", mcp_type=MCPType.EXCLUDE),
        RouteMap(tags={"internal"}, mcp_type=MCPType.EXCLUDE),
    ]

    # ====================================================
    # 🔹 Combinar OpenAPI
    # ====================================================
    yaml_files = glob.glob("openapi-all/*.yaml") + glob.glob("openapi-all/*.yml")
    combined_paths = {}
    combined_tags = []
    info = {"title": "Zoho Books AI Agent API", "version": "1.0.0"}

    for path in yaml_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                spec = yaml.safe_load(f)

            if not spec or not spec.get("paths"):
                logger.warning(f"⚠️ El archivo {path} no contiene paths válidos.")
                continue

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

    return FastMCP.from_openapi(
        openapi_spec=combined_spec,
        client=client,
        route_maps=route_maps,
        name="zoho-mcp-ai-agent",
    )


# ====================================================
# 🔹 Inicializar MCP
# ====================================================
try:
    logger.info("🔄 Initializing AI Agent MCP server...")
    mcp = build_mcp()
    logger.info("✅ MCP server initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing MCP server: {e}")
    raise e


# ====================================================
# 🔹 Ejecutar MCP
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
                "💡 Port 8080 ocupado → liberar con:\n   lsof -ti:8080 | xargs kill -9"
            )
