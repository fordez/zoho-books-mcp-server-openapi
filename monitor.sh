#!/bin/bash

# Script de monitoreo del servidor MCP
# Guárdalo como monitor.sh y hazlo ejecutable: chmod +x monitor.sh

echo "🔍 Monitoreando servidor MCP..."
echo "================================"

# Verificar estado del contenedor
echo ""
echo "📦 Estado del contenedor:"
docker compose ps

# Verificar salud del servicio
echo ""
echo "🏥 Health check:"
curl -s http://localhost:8080/health || echo "❌ Servicio no responde"

# Uso de recursos
echo ""
echo "💻 Uso de recursos:"
docker stats --no-stream zoho-mcp-server

# Últimos logs
echo ""
echo "📋 Últimos 20 logs:"
docker compose logs --tail=20

# Verificar conexiones activas
echo ""
echo "🔌 Conexiones activas al puerto 8080:"
netstat -an | grep :8080 | grep ESTABLISHED | wc -l

# Espacio en disco
echo ""
echo "💾 Espacio en disco:"
df -h /

echo ""
echo "================================"
echo "✅ Monitoreo completado"
