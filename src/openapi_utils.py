import logging
from typing import Dict

logger = logging.getLogger(__name__)


def generate_dynamic_request_schema(operation_id: str, operation: dict) -> dict:
    """
    Genera un schema dinámico basado en la descripción y parámetros del endpoint.
    Extrae campos comunes de Zoho Books y crea un schema flexible.
    """
    
    # Schema base genérico pero con estructura
    base_schema = {
        "type": "object",
        "additionalProperties": True,
        "description": operation.get("description", f"Request body for {operation_id}"),
        "properties": {},
    }
    
    # Detectar el tipo de entidad por el operation_id
    entity_type = None
    if "contact" in operation_id:
        entity_type = "contact"
    elif "invoice" in operation_id:
        entity_type = "invoice"
    elif "bill" in operation_id:
        entity_type = "bill"
    elif "item" in operation_id:
        entity_type = "item"
    elif "expense" in operation_id:
        entity_type = "expense"
    elif "estimate" in operation_id:
        entity_type = "estimate"
    elif "sales_order" in operation_id or "salesorder" in operation_id:
        entity_type = "sales_order"
    elif "purchase_order" in operation_id or "purchaseorder" in operation_id:
        entity_type = "purchase_order"
    elif "payment" in operation_id:
        entity_type = "payment"
    elif "vendor" in operation_id:
        entity_type = "vendor"
    
    # Agregar propiedades comunes según el tipo de entidad
    if entity_type == "contact":
        base_schema["properties"] = {
            "contact_name": {
                "type": "string",
                "description": "Display name of the contact",
            },
            "company_name": {"type": "string", "description": "Company name"},
            "contact_type": {"type": "string", "enum": ["customer", "vendor", "both"]},
            "contact_persons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "phone": {"type": "string"},
                        "is_primary_contact": {"type": "boolean"},
                    },
                },
            },
            "billing_address": {
                "type": "object",
                "properties": {
                    "attention": {"type": "string"},
                    "address": {"type": "string"},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "zip": {"type": "string"},
                    "country": {"type": "string"},
                },
            },
            "shipping_address": {
                "type": "object",
                "properties": {
                    "attention": {"type": "string"},
                    "address": {"type": "string"},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "zip": {"type": "string"},
                    "country": {"type": "string"},
                },
            },
            "currency_id": {"type": "string"},
            "payment_terms": {"type": "integer"},
            "notes": {"type": "string"},
            "custom_fields": {"type": "array"},
        }
        base_schema["required"] = ["contact_name"]

    elif entity_type in ["invoice", "estimate", "sales_order"]:
        base_schema["properties"] = {
            "customer_id": {"type": "string", "description": "Customer ID"},
            "date": {
                "type": "string",
                "format": "date",
                "description": "Document date",
            },
            "due_date": {"type": "string", "format": "date"},
            "reference_number": {"type": "string"},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "rate": {"type": "number"},
                        "quantity": {"type": "number"},
                        "discount": {"type": "number"},
                        "tax_id": {"type": "string"},
                    },
                },
            },
            "notes": {"type": "string"},
            "terms": {"type": "string"},
            "custom_fields": {"type": "array"},
        }
        base_schema["required"] = ["customer_id", "line_items"]

    elif entity_type in ["bill", "purchase_order"]:
        base_schema["properties"] = {
            "vendor_id": {"type": "string", "description": "Vendor ID"},
            "date": {"type": "string", "format": "date"},
            "due_date": {"type": "string", "format": "date"},
            "reference_number": {"type": "string"},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "rate": {"type": "number"},
                        "quantity": {"type": "number"},
                        "account_id": {"type": "string"},
                    },
                },
            },
            "notes": {"type": "string"},
            "custom_fields": {"type": "array"},
        }
        base_schema["required"] = ["vendor_id", "line_items"]

    elif entity_type == "item":
        base_schema["properties"] = {
            "name": {"type": "string", "description": "Item name"},
            "rate": {"type": "number", "description": "Item rate/price"},
            "description": {"type": "string"},
            "account_id": {"type": "string"},
            "tax_id": {"type": "string"},
            "unit": {"type": "string"},
            "is_taxable": {"type": "boolean"},
            "sku": {"type": "string"},
        }
        base_schema["required"] = ["name"]

    elif entity_type == "expense":
        base_schema["properties"] = {
            "account_id": {"type": "string", "description": "Expense account ID"},
            "date": {"type": "string", "format": "date"},
            "amount": {"type": "number"},
            "vendor_id": {"type": "string"},
            "customer_id": {"type": "string"},
            "currency_id": {"type": "string"},
            "reference_number": {"type": "string"},
            "description": {"type": "string"},
            "is_billable": {"type": "boolean"},
        }
        base_schema["required"] = ["account_id", "amount", "date"]

    elif entity_type == "payment":
        is_vendor_payment = "vendor" in operation_id
        base_schema["properties"] = {
            "vendor_id" if is_vendor_payment else "customer_id": {"type": "string"},
            "payment_mode": {"type": "string"},
            "amount": {"type": "number"},
            "date": {"type": "string", "format": "date"},
            "reference_number": {"type": "string"},
            "description": {"type": "string"},
            "bills" if is_vendor_payment else "invoices": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "bill_id" if is_vendor_payment else "invoice_id": {
                            "type": "string"
                        },
                        "amount_applied": {"type": "number"},
                    },
                },
            },
        }
        base_schema["required"] = [
            "vendor_id" if is_vendor_payment else "customer_id",
            "amount",
        ]

    logger.debug(
        f"   🔧 Generated dynamic schema for {operation_id} (entity: {entity_type})"
    )
    return base_schema


def add_missing_request_schemas(spec: dict) -> dict:
    """
    Recorre TODOS los endpoints POST/PUT/PATCH y genera schemas dinámicamente
    para aquellos que tienen referencias rotas o schemas vacíos.
    """
    
    if "components" not in spec:
        spec["components"] = {}
    if "schemas" not in spec["components"]:
        spec["components"]["schemas"] = {}
    
    schemas = spec["components"]["schemas"]
    schemas_added = 0
    
    # Recorrer todos los paths y buscar operaciones que necesiten schemas
    for path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in ["post", "put", "patch"]:
                continue
            
            operation_id = operation.get("operationId")
            if not operation_id:
                continue
            
            # Verificar si tiene requestBody con $ref
            request_body = operation.get("requestBody", {})
            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema", {})
            
            # Si tiene $ref, extraer el nombre del schema
            if "$ref" in schema:
                ref = schema["$ref"]
                schema_name = ref.split("/")[-1]  # Obtener el nombre del schema
                
                # Si el schema no existe, crearlo dinámicamente
                if schema_name not in schemas:
                    logger.info(
                        f"   🔧 Creating dynamic schema for: {schema_name} (from {operation_id})"
                    )
                    schemas[schema_name] = generate_dynamic_request_schema(
                        operation_id, operation
                    )
                    schemas_added += 1
    
    logger.info(f"✅ Added {schemas_added} dynamic request schemas")
    return spec


def filter_openapi_paths(spec: dict, allowed_tools: set) -> dict:
    """
    Filtra los paths del OpenAPI para incluir solo allowed_tools.
    Los schemas faltantes ya fueron agregados por add_missing_request_schemas().
    """
    logger.info("🔍 Starting OpenAPI paths filtering...")

    if not spec or "paths" not in spec:
        logger.warning("⚠️ No paths found in OpenAPI spec")
        return spec

    filtered_paths = {}
    included_count = 0
    excluded_count = 0

    for path, path_item in spec.get("paths", {}).items():
        filtered_path_item = {}

        # Copiar keys que NO son métodos HTTP (como 'parameters')
        for key, value in path_item.items():
            if key.lower() not in ["get", "post", "put", "patch", "delete"]:
                filtered_path_item[key] = value

        # Filtrar métodos HTTP
        for method in ["get", "post", "put", "patch", "delete"]:
            if method not in path_item:
                continue
            
            operation = path_item[method]
            operation_id = operation.get("operationId")

            if operation_id in allowed_tools:
                filtered_path_item[method] = operation
                included_count += 1
                logger.debug(f"✅ Including: {operation_id} ({method.upper()} {path})")
            else:
                excluded_count += 1
                logger.debug(f"⏭️  Skipping: {operation_id}")

        # Solo agregar el path si tiene al menos UN método HTTP
        has_http_method = any(m in filtered_path_item for m in ["get", "post", "put", "patch", "delete"])
        if has_http_method:
            filtered_paths[path] = filtered_path_item

    logger.info(
        f"✅ Filtering complete: {included_count} included, {excluded_count} excluded"
    )
    spec["paths"] = filtered_paths
    return spec


def remove_all_refs_from_schemas(spec: dict) -> dict:
    """
    🔥 SOLUCIÓN AL ERROR DE SCHEMA - CAPA 2
    
    Recorre todos los schemas y convierte las referencias $ref en definiciones inline.
    Esto elimina el problema de referencias rotas.
    """
    
    if "components" not in spec or "schemas" not in spec["components"]:
        logger.info("⏭️ No schemas found to clean")
        return spec
    
    schemas = spec["components"]["schemas"]
    
    def replace_refs_recursive(obj, depth=0):
        """Reemplaza todas las referencias $ref recursivamente con tipos básicos."""
        if depth > 10:
            logger.warning(f"⚠️ Max depth reached in schema resolution")
            return {"type": "string"}
        
        if isinstance(obj, dict):
            if "$ref" in obj:
                logger.debug(f"   🔧 Replaced $ref: {obj['$ref']} -> type: string")
                return {"type": "string"}
            else:
                return {k: replace_refs_recursive(v, depth + 1) 
                       for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_refs_recursive(item, depth + 1) 
                   for item in obj]
        else:
            return obj
    
    # Aplicar a todos los schemas
    logger.info("🔧 Removing all $ref from response schemas...")
    cleaned_count = 0
    total_refs = 0
    
    for schema_name, schema_def in list(schemas.items()):
        original_str = str(schema_def)
        original_refs = original_str.count("$ref")
        
        if original_refs > 0:
            cleaned = replace_refs_recursive(schema_def)
            schemas[schema_name] = cleaned
            cleaned_count += 1
            total_refs += original_refs
            logger.debug(f"   ✅ Cleaned {schema_name}: removed {original_refs} $ref")
    
    logger.info(f"✅ Cleaned {cleaned_count} schemas, removed {total_refs} total $ref")
    return spec


def fix_parameter_schemas(spec: dict) -> dict:
    """
    🔥 SOLUCIÓN ADICIONAL - Arregla esquemas de parámetros
    
    FastMCP valida que parámetros como 'page' y 'per_page' sean strings,
    pero los OpenAPI los definen como integers. Esta función los convierte.
    """
    logger.info("🔧 Fixing parameter schemas...")
    fixed_count = 0
    
    for path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue
            
            # Arreglar parámetros
            parameters = operation.get("parameters", [])
            for param in parameters:
                if "schema" in param:
                    schema = param["schema"]
                    # Si tiene type integer, convertir a string para FastMCP
                    if schema.get("type") == "integer":
                        schema["type"] = "string"
                        fixed_count += 1
                        logger.debug(f"   🔧 Fixed parameter '{param.get('name')}' in {operation.get('operationId')}")
    
    logger.info(f"✅ Fixed {fixed_count} parameter schemas")
    return spec


def fix_parameter_schemas(spec: dict) -> dict:
    """
    🔥 SOLUCIÓN ADICIONAL - Arregla esquemas de parámetros
    
    FastMCP valida que parámetros como 'page' y 'per_page' sean strings,
    pero los OpenAPI los definen como integers. Esta función los convierte.
    """
    logger.info("🔧 Fixing parameter schemas...")
    fixed_count = 0
    
    for path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue
            
            # Arreglar parámetros
            parameters = operation.get("parameters", [])
            for param in parameters:
                if "schema" in param:
                    schema = param["schema"]
                    # Si tiene type integer, convertir a string para FastMCP
                    if schema.get("type") == "integer":
                        schema["type"] = "string"
                        fixed_count += 1
                        logger.debug(f"   🔧 Fixed parameter '{param.get('name')}' in {operation.get('operationId')}")
    
    logger.info(f"✅ Fixed {fixed_count} parameter schemas")
    return spec


def fix_parameter_schemas(spec: dict) -> dict:
    """
    🔥 SOLUCIÓN ADICIONAL - Arregla esquemas de parámetros
    
    FastMCP valida que parámetros como 'page' y 'per_page' sean strings,
    pero los OpenAPI los definen como integers. Esta función los convierte.
    """
    logger.info("🔧 Fixing parameter schemas...")
    fixed_count = 0
    
    for path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue
            
            # Arreglar parámetros
            parameters = operation.get("parameters", [])
            for param in parameters:
                if "schema" in param:
                    schema = param["schema"]
                    # Si tiene type integer, convertir a string para FastMCP
                    if schema.get("type") == "integer":
                        schema["type"] = "string"
                        fixed_count += 1
                        logger.debug(f"   🔧 Fixed parameter '{param.get('name')}' in {operation.get('operationId')}")
    
    logger.info(f"✅ Fixed {fixed_count} parameter schemas")
    return spec


def fix_parameter_schemas(spec: dict) -> dict:
    """
    🔥 SOLUCIÓN ADICIONAL - Arregla esquemas de parámetros
    
    FastMCP valida que parámetros como 'page' y 'per_page' sean strings,
    pero los OpenAPI los definen como integers. Esta función los convierte.
    """
    logger.info("🔧 Fixing parameter schemas...")
    fixed_count = 0
    
    for path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue
            
            # Arreglar parámetros
            parameters = operation.get("parameters", [])
            for param in parameters:
                if "schema" in param:
                    schema = param["schema"]
                    # Si tiene type integer, convertir a string para FastMCP
                    if schema.get("type") == "integer":
                        schema["type"] = "string"
                        fixed_count += 1
                        logger.debug(f"   🔧 Fixed parameter '{param.get('name')}' in {operation.get('operationId')}")
    
    logger.info(f"✅ Fixed {fixed_count} parameter schemas")
    return spec


def fix_parameter_schemas(spec: dict) -> dict:
    """
    🔥 SOLUCIÓN ADICIONAL - Arregla esquemas de parámetros
    
    FastMCP valida que parámetros como 'page' y 'per_page' sean strings,
    pero los OpenAPI los definen como integers. Esta función los convierte.
    """
    logger.info("🔧 Fixing parameter schemas...")
    fixed_count = 0
    
    for path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue
            
            # Arreglar parámetros
            parameters = operation.get("parameters", [])
            for param in parameters:
                if "schema" in param:
                    schema = param["schema"]
                    # Si tiene type integer, convertir a string para FastMCP
                    if schema.get("type") == "integer":
                        schema["type"] = "string"
                        fixed_count += 1
                        logger.debug(f"   🔧 Fixed parameter '{param.get('name')}' in {operation.get('operationId')}")
    
    logger.info(f"✅ Fixed {fixed_count} parameter schemas")
    return spec
