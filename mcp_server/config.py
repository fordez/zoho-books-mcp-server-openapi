import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Cargar .env desde la raíz del proyecto
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")


class Config:
    """Configuración del servidor MCP"""

    # OAuth Server URL
    oauth_server_url = os.getenv("OAUTH_SERVER_URL", "http://localhost:8081")

    # MCP Server Config
    mcp_host = os.getenv("MCP_HOST", "0.0.0.0")
    mcp_port = int(os.getenv("MCP_PORT", "8080"))

    @classmethod
    def validate(cls):
        """Valida que la configuración esté completa"""
        if not cls.oauth_server_url:
            raise ValueError("OAUTH_SERVER_URL is required in .env")

        logger.info(f"✅ Config loaded:")
        logger.info(f"   OAuth Server: {cls.oauth_server_url}")
        logger.info(f"   MCP Host: {cls.mcp_host}")
        logger.info(f"   MCP Port: {cls.mcp_port}")
