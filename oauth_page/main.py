import os
import sys
from pathlib import Path

from fastapi import FastAPI

# Add parent directory (project root) to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.routes import setup_routes

from shared.token_db import get_db

# Load env vars
MCP_PORT = int(os.getenv("MCP_PORT", "8080"))
OAUTH_PORT = int(os.getenv("OAUTH_PORT", "8081"))

# Initialize FastAPI app
app = FastAPI()

# Initialize database
db = get_db()

# Setup routes
setup_routes(app, db)


if __name__ == "__main__":
    import uvicorn

    print("🚀 OAuth Server starting...")
    print(f"📍 OAuth Port: {OAUTH_PORT}")
    print(f"📍 MCP Port: {MCP_PORT}")
    print(f"🌐 Access: http://localhost:{OAUTH_PORT}")

    uvicorn.run(app, host="0.0.0.0", port=OAUTH_PORT)
