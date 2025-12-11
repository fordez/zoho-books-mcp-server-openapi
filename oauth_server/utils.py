from fastapi import Request


def get_base_url(request: Request) -> str:
    """
    Detecta el host y esquema automáticamente desde la petición.
    Funciona con localhost, ngrok, dominios reales, etc.
    """
    # Detectar esquema (http o https)
    scheme = request.url.scheme

    # Obtener host (puede ser localhost, ngrok, dominio real)
    host = request.headers.get("host", "").split(":")[0]

    # Si no hay host en headers, usar el de la URL
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
        parts = api_domain.split("//")[1].split(".")
        # Handle special case for .com.au
        if len(parts) == 4:  # ["www", "zohoapis", "com", "au"]
            return f"{parts[2]}.{parts[3]}"  # "com.au"
        else:  # ["www", "zohoapis", "in"]
            return parts[2] if len(parts) > 2 else "com"
    return "com"
