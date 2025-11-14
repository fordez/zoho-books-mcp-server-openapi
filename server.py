import asyncio
import glob
import os

import httpx
import yaml
from fastmcp import FastMCP
from fastmcp.experimental.server.openapi import MCPType, RouteMap

from config import Config


# 🔹 Función para obtener token de Zoho
async def get_access_token():
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": Config.refresh_token,
        "client_id": Config.client_id,
        "client_secret": Config.client_secret,
        "grant_type": "refresh_token",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data)
        print("🔹 Status code:", resp.status_code)
        print("🔹 Response:", resp.text)
        resp.raise_for_status()
        res = resp.json()
        if "access_token" not in res:
            raise Exception(f"No access token obtained: {res}")
        return res["access_token"]


# 🔹 Construcción del objeto MCP
async def build_mcp():
    access_token = await get_access_token()
    print("🔐 New access token obtained")

    client = httpx.AsyncClient(
        base_url=Config.base_url,
        headers={
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json;charset=UTF-8",
            "organization_id": Config.organization_id,
        },
        timeout=30.0,
    )

    route_maps = [
        RouteMap(pattern=r"^/admin/.*", mcp_type=MCPType.EXCLUDE),
        RouteMap(tags={"internal"}, mcp_type=MCPType.EXCLUDE),
        RouteMap(methods=["POST", "PUT", "PATCH", "DELETE"], mcp_type=MCPType.TOOL),
        RouteMap(methods=["GET"], mcp_type=MCPType.RESOURCE),
    ]

    yaml_files = glob.glob("openapi-all/*.yaml") + glob.glob("openapi-all/*.yml")
    combined_paths = {}
    combined_tags = []
    info = {"title": "Zoho Books Combined API", "version": "1.0.0"}

    for path in yaml_files:
        with open(path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        if not spec or not spec.get("paths"):
            continue
        combined_paths.update(spec.get("paths", {}))
        combined_tags.extend(spec.get("tags", []))

    combined_spec = {
        "openapi": "3.0.0",
        "info": info,
        "paths": combined_paths,
        "tags": combined_tags,
        "servers": [{"url": Config.base_url}],
    }

    return FastMCP.from_openapi(
        openapi_spec=combined_spec, client=client, route_maps=route_maps
    )


# 🔹 Objeto global requerido por FastMCP Cloud
mcp: FastMCP | None = None


# 🔹 Inicialización async para FastMCP Cloud
async def init_mcp():
    global mcp
    if mcp is None:
        mcp = await build_mcp()


# 🔹 Ejecución local
if __name__ == "__main__":
    os.environ["FASTMCP_HOST"] = "0.0.0.0"
    os.environ["FASTMCP_PORT"] = "8080"

    async def main():
        global mcp
        if mcp is None:
            mcp = await build_mcp()
        print("🚀 MCP server ready at http://0.0.0.0:8080")
        await mcp.run(transport="http", host="0.0.0.0", port=8080)

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Error: {e}")
        if "address already in use" in str(e).lower():
            print("💡 Port 8080 is in use. Free it with: lsof -ti:8080 | xargs kill -9")
