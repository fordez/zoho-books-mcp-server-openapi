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
# 🤖 HERRAMIENTAS ESENCIALES PARA AI AGENT (85 tools)
# ====================================================
# Basado en patrones de agentes AI en contabilidad:
# - Automatización de workflows end-to-end
# - Procesamiento de documentos y extracción de datos
# - Reconciliación y matching automático
# - Detección de anomalías en tiempo real
# - Gestión de ciclo de vida completo de transacciones
# ====================================================

ALLOWED_TOOLS = {
    # ============================================
    # 🧾 INVOICES - Ciclo completo (12 tools)
    # ============================================
    # Agente necesita: buscar, crear, leer, actualizar, enviar
    "list_invoices",  # 🔍 Búsqueda/filtrado de facturas
    "get_invoice",  # 📄 Detalle completo
    "create_invoice",  # ➕ Generación automática
    "update_invoice",  # ✏️ Modificación
    "delete_invoice",  # 🗑️ Eliminación
    "email_invoice",  # 📧 Envío automatizado
    "mark_invoice_sent",  # ✅ Estado enviado
    "mark_invoice_void",  # ❌ Anulación
    # Gestión de pagos vinculados
    "list_invoice_payments",  # 💰 Pagos recibidos
    "apply_credits_to_invoice",  # 🔄 Aplicar créditos
    # Adjuntos para verificación
    "get_invoice_attachment",
    "add_invoice_attachment",
    # ============================================
    # 📋 BILLS - Cuentas por pagar (11 tools)
    # ============================================
    # Agente necesita: recepción, matching, pago
    "list_bills",  # 🔍 Búsqueda de facturas proveedor
    "get_bill",  # 📄 Detalle
    "create_bill",  # ➕ Registro automático (OCR)
    "update_bill",  # ✏️ Correcciones
    "delete_bill",  # 🗑️ Eliminación
    "mark_bill_void",  # ❌ Anulación
    "mark_bill_open",  # 🔓 Reabrir
    # Pagos y reconciliación
    "list_bill_payments",  # 💰 Historial de pagos
    "apply_credits_to_bill",  # 🔄 Aplicar créditos
    # Adjuntos (crítico para OCR/verificación)
    "get_bill_attachment",
    "add_bill_attachment",
    # ============================================
    # 👥 CONTACTS - Clientes/Proveedores (10 tools)
    # ============================================
    # Agente necesita: verificar, crear, actualizar
    "list_contacts",  # 🔍 Búsqueda de contactos
    "get_contact",  # 📄 Información completa
    "create_contact",  # ➕ Registro automático
    "update_contact",  # ✏️ Actualización de datos
    "delete_contact",  # 🗑️ Eliminación
    "mark_contact_active",  # ✅ Activar
    "mark_contact_inactive",  # ⏸️ Desactivar
    # Direcciones para matching/validación
    "add_contact_address",
    "update_contact_address",
    "delete_contact_address",
    # ============================================
    # 📦 ITEMS - Productos/Servicios (8 tools)
    # ============================================
    # Agente necesita: catálogo, pricing, inventory
    "list_items",  # 🔍 Búsqueda de productos
    "get_item",  # 📄 Detalle completo
    "create_item",  # ➕ Nuevo producto
    "update_item",  # ✏️ Actualizar precio/stock
    "delete_item",  # 🗑️ Eliminación
    "list_item_details",  # 📊 Detalles extendidos
    "mark_item_active",  # ✅ Activar
    "mark_item_inactive",  # ⏸️ Desactivar
    # ============================================
    # 💸 EXPENSES - Gastos (8 tools)
    # ============================================
    # Agente necesita: registro, categorización, adjuntos
    "list_expenses",  # 🔍 Búsqueda de gastos
    "get_expense",  # 📄 Detalle
    "create_expense",  # ➕ Registro automático
    "update_expense",  # ✏️ Corrección/categorización
    "delete_expense",  # 🗑️ Eliminación
    # Recibos (crítico para AI - OCR)
    "get_expense_receipt",
    "create_expense_receipt",
    "delete_expense_receipt",
    # ============================================
    # 💳 VENDOR PAYMENTS - Pagos a proveedores (6 tools)
    # ============================================
    # Agente necesita: programar, ejecutar, reconciliar
    "list_vendor_payments",  # 🔍 Historial de pagos
    "get_vendor_payment",  # 📄 Detalle de pago
    "create_vendor_payment",  # ➕ Registro de pago
    "update_vendor_payment",  # ✏️ Modificación
    "delete_vendor_payment",  # 🗑️ Eliminación
    "email_vendor_payment",  # 📧 Notificación
    # ============================================
    # 🏢 VENDORS - Gestión de proveedores (5 tools)
    # ============================================
    "list_vendors",  # 🔍 Búsqueda de proveedores
    "get_vendor",  # 📄 Información completa
    "create_vendor",  # ➕ Registro automático
    "update_vendor",  # ✏️ Actualización
    "delete_vendor",  # 🗑️ Eliminación
    # ============================================
    # 📝 ESTIMATES - Cotizaciones (7 tools)
    # ============================================
    # Agente necesita: generar, enviar, tracking
    "list_estimates",  # 🔍 Búsqueda
    "get_estimate",  # 📄 Detalle
    "create_estimate",  # ➕ Generación automática
    "update_estimate",  # ✏️ Modificación
    "delete_estimate",  # 🗑️ Eliminación
    "mark_estimate_accepted",  # ✅ Aceptado (→ convertir)
    "email_estimate",  # 📧 Envío
    # ============================================
    # 🛒 SALES ORDERS - Órdenes de venta (7 tools)
    # ============================================
    "list_sales_orders",  # 🔍 Búsqueda
    "get_sales_order",  # 📄 Detalle
    "create_sales_order",  # ➕ Creación
    "update_sales_order",  # ✏️ Modificación
    "delete_sales_order",  # 🗑️ Eliminación
    "mark_sales_order_as_void",  # ❌ Anular
    "email_sales_order",  # 📧 Envío
    # ============================================
    # 🛍️ PURCHASE ORDERS - Órdenes de compra (6 tools)
    # ============================================
    "list_purchase_orders",  # 🔍 Búsqueda
    "get_purchase_order",  # 📄 Detalle
    "create_purchase_order",  # ➕ Creación
    "update_purchase_order",  # ✏️ Modificación
    "delete_purchase_order",  # 🗑️ Eliminación
    "list_purchase_order_comments",  # 💬 Seguimiento
    # ============================================
    # 👤 USERS - Gestión básica (3 tools)
    # ============================================
    "list_users",  # 🔍 Lista de usuarios
    "get_user",  # 📄 Info de usuario
    "get_current_user",  # 🔐 Usuario actual
    # ============================================
    # 🎯 PROJECTS - Seguimiento básico (2 tools)
    # ============================================
    # Solo lectura para tracking, no gestión compleja
    "list_projects",  # 🔍 Lista de proyectos
    "get_project",  # 📄 Detalle de proyecto
}

# Total: 85 tools optimizadas para AI Agent


# ====================================================
# 🔹 Obtener token Zoho (síncrono - solo para inicialización)
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
    """
    Filtra los paths del OpenAPI para incluir solo los operationId
    que están en ALLOWED_TOOLS
    """
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

            # Solo incluir si el operationId está en la lista permitida
            if operation_id in ALLOWED_TOOLS:
                filtered_path_item[method] = operation
                included_count += 1
                logger.info(f"✅ Including: {operation_id}")
            else:
                excluded_count += 1
                logger.debug(f"⏭️  Skipping: {operation_id}")

        # Solo agregar el path si tiene operaciones permitidas
        if filtered_path_item:
            filtered_paths[path] = filtered_path_item

    logger.info(
        f"📊 Filtering complete: {included_count} included, {excluded_count} excluded"
    )
    spec["paths"] = filtered_paths
    return spec


# ====================================================
# 🔹 Construcción MCP ASÍNCRONA
# ====================================================
def build_mcp() -> FastMCP:
    access_token = get_access_token()

    # ⚠️ CRÍTICO: Usar AsyncClient para operaciones asíncronas
    client = httpx.AsyncClient(
        base_url=Config.base_url,
        headers={
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json;charset=UTF-8",
            "organization_id": Config.organization_id,
        },
        timeout=30.0,
    )

    # ====================================================
    # 🔹 Route maps básicos
    # ====================================================
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

    # ====================================================
    # 🔹 FILTRAR SPEC ANTES DE CREAR MCP
    # ====================================================
    logger.info(f"📋 Total paths before filtering: {len(combined_spec['paths'])}")
    combined_spec = filter_openapi_paths(combined_spec)
    logger.info(f"✅ Total paths after filtering: {len(combined_spec['paths'])}")
    logger.info(f"🎯 Total allowed tools: {len(ALLOWED_TOOLS)}")

    logger.info("🚀 Building MCP from filtered OpenAPI spec")

    # ====================================================
    # 🔹 CREAR MCP
    # ====================================================
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
