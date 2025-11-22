#!/bin/bash

# Nombre del script: deploy.sh
# Descripción: Actualiza el repositorio, reinicia el contenedor y sigue los logs

# Salir si hay un error
set -e

echo "🔹 Haciendo pull de la rama main..."
git pull origin main

echo "🔹 Deteniendo contenedores..."
docker compose down

echo "🔹 Levantando contenedores en modo detach y rebuild..."
docker compose up -d --build

echo "Url"
curl http://localhost:4040/api/tunnels
#echo "🔹 Mostrando logs en tiempo real..."
#docker compose logs -f
