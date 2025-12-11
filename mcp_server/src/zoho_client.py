import json
import logging
import re
from typing import Any
from urllib.parse import unquote

import httpx

logger = logging.getLogger(__name__)


def simplify_zoho_response(response_json):
    """Convierte code a string y simplifica respuestas"""
    if not isinstance(response_json, dict):
        return response_json
    
    # 🔥 CRÍTICO: Convertir code a string SIEMPRE
    if "code" in response_json:
        response_json["code"] = str(response_json["code"])
        logger.info(f"✅ Converted code to string: {response_json['code']}")
    
    # Si es lista, devolver con code convertido
    list_keys = ["invoices", "bills", "contacts", "items", "expenses", 
                 "estimates", "sales_orders", "purchase_orders", "payments"]
    if any(key in response_json for key in list_keys):
        logger.info(f"📋 List response detected, returning with code converted")
        return response_json
    
    # Simplificar respuestas de objetos únicos
    main_keys = ["contact", "invoice", "item", "bill", "estimate", 
                 "expense", "sales_order", "purchase_order", "payment",
                 "vendor_payment", "user", "project"]
    
    for key in main_keys:
        if key in response_json:
            main_object = response_json[key]
            simplified = {
                "code": str(response_json.get("code", 0)),
                "message": response_json.get("message", "Success"),
                f"{key}_id": main_object.get(f"{key}_id"),
                "full_data": main_object
            }
            logger.info(f"✂️ Simplified {key} response")
            return simplified
    
    return response_json


class ZohoAsyncClient(httpx.AsyncClient):
    """Cliente personalizado para Zoho Books API"""

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        logger.info("=" * 80)
        logger.info(f"🔵 {method} {url}")

        # Fix path parameters
        decoded_url = unquote(url)
        placeholders = re.findall(r"\{([^}]+)\}", decoded_url)

        if placeholders:
            for placeholder in placeholders:
                value = None
                if placeholder in kwargs:
                    value = kwargs.pop(placeholder)
                elif "params" in kwargs and placeholder in kwargs["params"]:
                    value = kwargs["params"].pop(placeholder)
                elif "json" in kwargs and isinstance(kwargs["json"], dict) and placeholder in kwargs["json"]:
                    value = kwargs["json"].pop(placeholder)
                
                if value:
                    decoded_url = decoded_url.replace(f"{{{placeholder}}}", str(value))
            url = decoded_url

        # Process JSON body for POST/PUT/PATCH
        if method.upper() in ["POST", "PUT", "PATCH"] and "json" in kwargs:
            json_data = kwargs.get("json")
            if isinstance(json_data, dict):
                for key, value in json_data.items():
                    if isinstance(value, str) and value.strip().startswith(("[", "{")):
                        try:
                            json_data[key] = json.loads(value)
                        except:
                            pass

        response = await super().request(method, url, **kwargs)

        logger.info(f"📊 Status: {response.status_code}")

        # 🔥 CRÍTICO: Simplificar respuesta SIEMPRE
        try:
            response_json = response.json()
            logger.info(f"📄 Original response has 'code': {response_json.get('code')}")
            
            simplified = simplify_zoho_response(response_json)
            
            logger.info(f"📄 Simplified response has 'code': {simplified.get('code')}")
            
            # Reemplazar contenido
            response._content = json.dumps(simplified, ensure_ascii=False).encode("utf-8")
            logger.info(f"✅ Response content replaced")

        except Exception as e:
            logger.error(f"❌ Error simplifying response: {e}")

        logger.info("=" * 80)

        return response
