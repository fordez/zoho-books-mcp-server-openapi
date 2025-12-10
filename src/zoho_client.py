import json
import logging
import re
from typing import Any
from urllib.parse import unquote

import httpx

logger = logging.getLogger(__name__)


def simplify_zoho_response(response_json):
    """
    🔥 SOLUCIÓN AL ERROR DE SCHEMA
    
    Simplifica cualquier respuesta de Zoho Books a una estructura flat.
    Esto evita problemas con esquemas anidados y referencias $ref rotas.
    """
    if not isinstance(response_json, dict):
        return response_json
    
    # Si es una lista (ej: list_invoices), no simplificar
    if any(key.endswith("s") for key in response_json.keys() if key in [
        "invoices", "bills", "contacts", "items", "expenses", 
        "estimates", "sales_orders", "purchase_orders", "payments"
    ]):
        return response_json
    
    # Extraer el objeto principal (contact, invoice, item, etc.)
    main_object = None
    main_key = None
    
    for key in ["contact", "invoice", "item", "bill", "estimate", 
                "expense", "sales_order", "purchase_order", "payment",
                "vendor_payment", "user", "project", "salesorder",
                "purchaseorder"]:
        if key in response_json:
            main_object = response_json[key]
            main_key = key
            break
    
    if not main_object:
        # No hay objeto anidado, devolver tal cual
        return response_json
    
    # Extraer solo campos esenciales del objeto principal
    simplified = {
        "code": response_json.get("code", 0),
        "message": response_json.get("message", "Success"),
    }
    
    # Agregar ID principal si existe
    id_key = f"{main_key}_id"
    if id_key in main_object:
        simplified[id_key] = main_object[id_key]
    
    # Agregar campos comunes útiles
    common_fields = [
        "name", "status", "contact_name", "company_name", "contact_type",
        "invoice_number", "bill_number", "estimate_number",
        "salesorder_number", "purchaseorder_number",
        "total", "balance", "amount",
        "date", "due_date", "created_time",
        "customer_name", "vendor_name", "customer_id", "vendor_id",
        "email", "phone", "rate", "description",
        "currency_code", "payment_terms", "reference_number"
    ]
    
    for field in common_fields:
        if field in main_object:
            simplified[field] = main_object[field]
    
    # Mantener el objeto completo bajo una key 'full_data' por si se necesita
    simplified["full_data"] = main_object
    
    logger.debug(f"✂️ Simplified {main_key} response: {len(str(main_object))} -> {len(str(simplified))} chars")
    
    return simplified


class ZohoAsyncClient(httpx.AsyncClient):
    """
    Cliente personalizado que transforma requests para Zoho Books API.
    Zoho requiere que POST/PUT envíen datos como JSON directo.
    También arregla path parameters que FastMCP no reemplaza correctamente.
    
    🔥 ACTUALIZACIÓN: Ahora simplifica TODAS las respuestas para evitar
    errores de validación de schema con referencias $ref rotas.
    """

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """
        Intercepta y transforma requests para el formato de Zoho Books.

        GET: Mantiene query params normales
        POST/PUT/PATCH: Envía JSON body directo con Content-Type: application/json

        ADEMÁS: Arregla path parameters que FastMCP no reemplaza
        Ejemplo: /contacts/{contact_id} -> /contacts/123456789
        
        🔥 NUEVO: Simplifica todas las respuestas antes de devolverlas
        """

        logger.info("=" * 80)
        logger.info(f"🔵 INCOMING REQUEST")
        logger.info(f"📍 Method: {method}")
        logger.info(f"🔗 URL (original): {url}")

        # 🔥 FIX PATH PARAMETERS - BÚSQUEDA EXHAUSTIVA
        decoded_url = unquote(url)
        placeholders = re.findall(r"\{([^}]+)\}", decoded_url)

        if placeholders:
            logger.info(f"🔍 Found path parameters: {placeholders}")

            # 🔥 NUEVO: Buscar en TODOS los kwargs incluyendo nivel superior
            all_kwargs = dict(kwargs)
            
            # Agregar argumentos del nivel superior que FastMCP podría enviar
            for key, value in list(kwargs.items()):
                if key not in ['params', 'json', 'data', 'headers', 'timeout']:
                    # Podría ser un path parameter enviado como kwarg directo
                    all_kwargs[key] = value

            for placeholder in placeholders:
                value = None

                # 1. Buscar como kwarg directo (FastMCP a veces envía así)
                if placeholder in kwargs:
                    value = kwargs.pop(placeholder)
                    logger.info(f"   ✅ Found {placeholder} in direct kwargs: {value}")

                # 2. Buscar en params de query
                elif "params" in kwargs and placeholder in kwargs["params"]:
                    value = kwargs["params"].pop(placeholder)
                    logger.info(f"   ✅ Found {placeholder} in params: {value}")

                # 3. Buscar en el body JSON
                elif (
                    "json" in kwargs
                    and isinstance(kwargs["json"], dict)
                    and placeholder in kwargs["json"]
                ):
                    value = kwargs["json"].pop(placeholder)
                    logger.info(f"   ✅ Found {placeholder} in json body: {value}")

                # 4. Buscar en data
                elif (
                    "data" in kwargs
                    and isinstance(kwargs["data"], dict)
                    and placeholder in kwargs["data"]
                ):
                    value = kwargs["data"].pop(placeholder)
                    logger.info(f"   ✅ Found {placeholder} in data: {value}")

                # Reemplazar en la URL
                if value:
                    old_url = decoded_url
                    decoded_url = decoded_url.replace(f"{{{placeholder}}}", str(value))
                    logger.info(f"   🔧 Replaced: {old_url} -> {decoded_url}")
                else:
                    logger.warning(
                        f"   ⚠️ No value found for path parameter: {placeholder}"
                    )
                    logger.warning(f"   📦 Available kwargs: {list(kwargs.keys())}")
                    logger.warning(f"   📦 Params: {kwargs.get('params', {})}")

            url = decoded_url
            logger.info(f"🔗 URL (fixed): {url}")

        logger.info(f"📦 kwargs keys: {kwargs.keys()}")

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

        # Si hay JSON body en POST/PUT/PATCH, procesar para Zoho
        if method.upper() in ["POST", "PUT", "PATCH"]:
            logger.info(f"🔄 Processing {method} request for Zoho format...")

            if "json" in kwargs:
                json_data = kwargs.pop("json")
                logger.info(f"✅ Found JSON data in kwargs")
                logger.info(f"📦 JSON data content: {json_data}")
                logger.info(f"📦 JSON data type: {type(json_data)}")

                if json_data is None:
                    logger.error("❌ JSON data is None!")
                    raise ValueError(f"Cannot {method}: JSON data is None")

                if json_data == {}:
                    logger.warning("⚠️ JSON data is empty dict!")

                # 🔥 PARSEAR strings JSON a objetos nativos
                if isinstance(json_data, dict):
                    for key, value in json_data.items():
                        if isinstance(value, str):
                            if value.strip().startswith(("[", "{")):
                                try:
                                    json_data[key] = json.loads(value)
                                    logger.info(
                                        f"   🔧 Parsed {key} from string to object"
                                    )
                                except json.JSONDecodeError:
                                    logger.warning(
                                        f"   ⚠️ Could not parse {key}, keeping as string"
                                    )

                logger.info(
                    f"📝 JSON Body (direct): {json.dumps(json_data, ensure_ascii=False)}"
                )

                kwargs["json"] = json_data
                logger.info(
                    f"✅ Using 'json' parameter - httpx will set Content-Type: application/json"
                )
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
                f"📄 Response Body (JSON - first 500 chars): {json.dumps(response_json, indent=2, ensure_ascii=False)[:500]}..."
            )

            # 🔥 SIMPLIFICAR RESPONSE PARA FASTMCP - SOLUCIÓN AL ERROR DE SCHEMA
            simplified = simplify_zoho_response(response_json)
            
            if simplified != response_json:
                logger.info(f"✂️ Response simplified for FastMCP")
                logger.info(f"✂️ Original size: {len(str(response_json))} chars")
                logger.info(f"✂️ Simplified size: {len(str(simplified))} chars")
                
                # Reemplazar el contenido de la respuesta
                response._content = json.dumps(simplified, ensure_ascii=False).encode("utf-8")

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

            logger.error(f"❌ Failed request details:")
            logger.error(f"   Method: {method}")
            logger.error(f"   URL: {url}")
            logger.error(f"   Final kwargs: {kwargs}")

        return response
