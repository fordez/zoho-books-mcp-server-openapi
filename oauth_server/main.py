import sys
from pathlib import Path

from fastapi import FastAPI

# Add parent directory to path to import shared module
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MCP_PORT, OAUTH_PORT
from routes import setup_routes

from shared.token_db import get_db

# Initialize FastAPI app
app = FastAPI()

# Initialize database
db = get_db()

# Setup all routes
setup_routes(app, db)


if __name__ == "__main__":
    import uvicorn

    print("🚀 OAuth Server starting...")
    print(f"📍 OAuth Port: {OAUTH_PORT}")
    print(f"📍 MCP Port: {MCP_PORT}")
    print(f"🌐 Access: http://localhost:{OAUTH_PORT}")

    uvicorn.run(app, host="0.0.0.0", port=OAUTH_PORT)
