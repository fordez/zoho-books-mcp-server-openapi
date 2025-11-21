FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos primero (para aprovechar cache)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de archivos
COPY . .

# Exponer puerto
EXPOSE 8080

# Variables de entorno por defecto
ENV FASTMCP_HOST=0.0.0.0
ENV FASTMCP_PORT=8080

# Comando de inicio
CMD ["python", "server.py"]
