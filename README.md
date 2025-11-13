# Zoho Books MCP Server

This project implements a **server-based MCP (Multimodal Communication Protocol) server** for Zoho Books using `FastMCP`. The server fetches access tokens using a **refresh token** and exposes all Zoho Books endpoints defined in OpenAPI YAML files.

---

## Features

- Server-based OAuth2 authentication (refresh token)
- Combines multiple OpenAPI YAML specs into a single MCP server
- Automatically generates MCP tools and resources from OpenAPI
- Customizable route maps for including/excluding endpoints
- Async HTTP client for Zoho API requests
- FastMCP server running on HTTP transport

---

## Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt`:

```txt
fastmcp
httpx
PyYAML
python-dotenv
Zoho Books credentials:

Client ID

Client Secret

Refresh Token

Organization ID

Zoho API base URL (e.g., https://www.zohoapis.com/books/v3)

Project Structure
bash
Copiar código
rava-crm-zoho/
│
├── server.py            # MCP server script
├── config.py            # Configuration file (loads .env)
├── openapi-all/         # Folder with all Zoho OpenAPI YAML files
├── .env                 # Environment variables
└── README.md
Environment Variables
Create a .env file with the following variables:

env
Copiar código
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_ORG_ID=your_organization_id
ZOHO_BASE_URL=https://www.zohoapis.com/books/v3
If your Zoho data center is India, just change ZOHO_BASE_URL to https://www.zohoapis.in/books/v3

Installation
Clone the repository:

bash
Copiar código
git clone https://github.com/yourusername/rava-crm-zoho.git
cd rava-crm-zoho
Create a Python virtual environment:

bash
Copiar código
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
Install dependencies:

bash
Copiar código
pip install -r requirements.txt
Add your .env file with Zoho credentials.

Add OpenAPI YAML files to openapi-all/.

Running the MCP Server
Start the server:

bash
Copiar código
python server.py
You should see output like:

arduino
Copiar código
🚀 Starting MCP server...
🔐 New access token obtained
✅ MCP server ready at http://0.0.0.0:8080
Using the MCP Server
You can connect to the MCP server using a FastMCP Client:

python
Copiar código
from fastmcp import Client
import asyncio

SERVER_URL = "http://localhost:8080/mcp"

async def main():
    client = Client(SERVER_URL)
    async with client:
        await client.ping()  # Check connection
        tools = await client.list_tools()
        print(f"Total tools: {len(tools)}")

asyncio.run(main())
Route Maps
The server defines route maps:

Exclude /admin/* endpoints

Exclude internal tags

Treat POST/PUT/PATCH/DELETE as tools

Treat GET as resources

You can customize this in server.py.

Notes
This server uses server-based OAuth only, no client-based flow.

Make sure port 8080 is free before running the server:

bash
Copiar código
lsof -ti:8080 | xargs kill -9
The server combines all OpenAPI YAML files under openapi-all/ into one MCP instance.

License
MIT License

Author
Fernando Ordoñez

pgsql
Copiar código

I can also make a **shorter, “quickstart” version** if you want something more concise for your repo homepage.  

Do you want me to create that too?
