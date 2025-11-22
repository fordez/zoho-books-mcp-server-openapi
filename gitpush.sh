#!/bin/bash

# Nombre del script: git_push.sh
# Descripción: Agrega cambios, hace commit con mensaje ingresado por el usuario y hace push a GitHub

# Salir si hay un error
set -e

# Preguntar al usuario por el mensaje de commit
read -p "📝 Ingresa el mensaje de commit: " commit_message

# Validar que no esté vacío
if [ -z "$commit_message" ]; then
  echo "❌ El mensaje de commit no puede estar vacío."
  exit 1
fi

echo "🔹 Agregando todos los cambios..."
git add .

echo "🔹 Haciendo commit..."
git commit -m "$commit_message"

echo "🔹 Haciendo push a la rama main..."
git push origin main

echo "✅ Push completado correctamente."
