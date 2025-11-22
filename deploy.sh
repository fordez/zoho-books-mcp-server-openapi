#!/bin/bash

# Nombre del script: deploy.sh
# Descripción: Actualiza el repositorio, reinicia el contenedor, espera y consulta el endpoint

# Salir si hay un error
set -e

echo "🔹 Haciendo pull de la rama main..."
git pull origin main

echo "🔹 Deteniendo contenedores..."
docker compose down

echo "🔹 Levantando contenedores en modo detach y rebuild..."
docker compose up -d --build

# Espera 5 segundos para que los contenedores terminen de iniciar
echo "⏳ Esperando 5 segundos para que los contenedores estén listos..."
sleep 5

echo "🔹 Consultando la URL del túnel..."
curl http://localhost:4040/api/tunnels

# Espera 2 segundos antes de seguir a los logs
#sleep 2

#echo "🔹 Mostrando logs en tiempo real..."
#docker compose logs -f
