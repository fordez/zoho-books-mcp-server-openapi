import time

import requests
from fastapi import Request


def get_base_url(request: Request) -> str:
    """
    Detecta automáticamente el esquema y host desde la petición.
    Funciona con localhost, ngrok, dominios reales, etc.
    """
    scheme = request.url.scheme
    host = request.headers.get("host", "").split(":")[0]

    if not host:
        host = request.url.hostname or "localhost"

    return f"{scheme}://{host}"


def extract_region_from_domain(api_domain: str) -> str:
    """
    Extrae la región del api_domain de Zoho.
    Ejemplos:
        https://www.zohoapis.com -> com
        https://www.zohoapis.in -> in
        https://www.zohoapis.com.au -> com.au
    """
    if ".zohoapis." in api_domain:
        domain = api_domain.split("//")[1]
        parts = domain.split(".")

        if len(parts) == 4:  # ["www", "zohoapis", "com", "au"]
            return f"{parts[2]}.{parts[3]}"
        elif len(parts) >= 3:  # ["www", "zohoapis", "in"]
            return parts[2]

    return "com"


def get_ngrok_public_url() -> str:
    """
    Obtiene la URL pública del túnel ngrok.
    Funciona en:
      - Localhost → llama a http://localhost:4040
      - Docker Compose → llama a http://ngrok:4040

    Retorna:
        str → URL pública (https://xxxxx.ngrok.io)
        None → si no fue posible obtenerla
    """
    urls_to_try = [
        "http://localhost:4040/api/tunnels",  # Modo local
        "http://ngrok:4040/api/tunnels",  # Modo Docker Compose
    ]

    for url in urls_to_try:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get("tunnels", [])

                for tunnel in tunnels:
                    public = tunnel.get("public_url")
                    if public:
                        return public.rstrip("/")
        except Exception:
            continue  # Intentar siguiente URL

    return None
