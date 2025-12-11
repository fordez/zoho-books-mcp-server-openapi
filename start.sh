#!/bin/bash
echo "🚀 Iniciando Zoho Books Multi-Tenant"

pkill -f "oauth_server/main.py" 2>/dev/null
pkill -f "mcp_server/server.py" 2>/dev/null
sleep 2

# OAuth Server
cd oauth_server
nohup python main.py > oauth.log 2>&1 &
cd ..

sleep 3

# MCP Server  
cd mcp_server
nohup python server.py > mcp.log 2>&1 &
cd ..

sleep 2

echo ""
echo "✅ OAuth Server: http://localhost:8081"
echo "✅ MCP Server: http://localhost:8080"
echo "🗄️  Database: $(pwd)/tokens.db"
echo ""
echo "📖 Conectar usuario: http://localhost:8081"
