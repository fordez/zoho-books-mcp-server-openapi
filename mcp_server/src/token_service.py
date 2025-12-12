import logging
import os
import time
from pathlib import Path
from threading import Lock
from typing import Dict

import httpx
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Cargar .env desde la raíz del proyecto
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")


class OAuthClient:
    """Cliente para obtener tokens desde el servidor OAuth"""

    def __init__(self, oauth_server_url: str = None):
        # Si no se pasa URL, leer del .env
        if oauth_server_url is None:
            oauth_server_url = os.getenv("OAUTH_SERVER_URL", "http://oauth-server:8081")

        self.oauth_server_url = oauth_server_url.rstrip("/")
        self._token_cache: Dict[str, any] = {
            "access_token": None,
            "organization_id": None,
            "api_domain": None,
            "region": None,
            "email": None,
            "company_name": None,
            "expires_at": 0,
        }
        self._lock = Lock()
        logger.info(f"🔗 OAuth Client initialized: {oauth_server_url}")

    def get_credentials(self) -> Dict[str, str]:
        """
        Obtiene las credenciales de la cuenta activa desde el servidor OAuth.
        Usa caché si el token es válido.
        """
        with self._lock:
            now = time.time()

            # Si hay token en caché y no ha expirado (5 min de margen), usarlo
            if self._token_cache["access_token"] and now < (
                self._token_cache["expires_at"] - 300
            ):
                logger.debug("✅ Using cached credentials")
                return self._token_cache

            # Obtener nuevas credenciales del servidor OAuth
            logger.info("🔐 Fetching fresh credentials from OAuth server...")

            try:
                with httpx.Client(timeout=30.0) as client:
                    resp = client.get(f"{self.oauth_server_url}/token")
                    resp.raise_for_status()
                    data = resp.json()

                # Actualizar caché
                self._token_cache.update(
                    {
                        "access_token": data["access_token"],
                        "organization_id": data["organization_id"],
                        "api_domain": data["api_domain"],
                        "region": data["region"],
                        "email": data.get("email", ""),
                        "company_name": data.get("company_name", ""),
                        "expires_at": now + 3600,  # 1 hora
                    }
                )

                logger.info(
                    f"✅ Credentials refreshed for: {data.get('company_name', 'Unknown')}"
                )
                logger.info(f"   📧 Email: {data.get('email', 'N/A')}")
                logger.info(f"   🌐 Region: {data.get('region', 'N/A')}")
                logger.info(f"   🏢 Org ID: {data['organization_id']}")

                return self._token_cache

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    error_msg = (
                        "❌ No active Zoho Books account found.\n"
                        f"   Please connect an account at: {self.oauth_server_url}"
                    )
                    logger.error(error_msg)
                    raise Exception(error_msg)
                else:
                    logger.error(
                        f"❌ OAuth server error: {e.response.status_code} - {e.response.text}"
                    )
                    raise
            except httpx.ConnectError as e:
                error_msg = (
                    f"❌ Cannot connect to OAuth server at {self.oauth_server_url}\n"
                    f"   Error: {str(e)}"
                )
                logger.error(error_msg)
                raise Exception(error_msg)
            except Exception as e:
                logger.error(f"❌ Failed to get credentials: {e}")
                raise

    def get_access_token(self) -> str:
        """Obtiene solo el access token"""
        return self.get_credentials()["access_token"]

    def get_organization_id(self) -> str:
        """Obtiene solo el organization ID"""
        return self.get_credentials()["organization_id"]

    def get_api_domain(self) -> str:
        """Obtiene el API domain (base URL)"""
        return self.get_credentials()["api_domain"]


# ============================================
# FUNCIONES DE COMPATIBILIDAD
# ============================================
# Estas funciones mantienen la compatibilidad con el código existente

_oauth_client = None


def _get_oauth_client() -> OAuthClient:
    """Singleton del cliente OAuth"""
    global _oauth_client
    if _oauth_client is None:
        _oauth_client = OAuthClient()
    return _oauth_client


def get_access_token() -> str:
    """
    Obtiene el access token desde el servidor OAuth.
    Esta función mantiene compatibilidad con el código existente.
    """
    client = _get_oauth_client()
    return client.get_access_token()


def get_credentials() -> Dict[str, str]:
    """
    Obtiene todas las credenciales (token, org_id, api_domain, etc.)
    """
    client = _get_oauth_client()
    return client.get_credentials()
