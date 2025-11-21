# 🚀 Guía Completa: Deployment de Servidor MCP Zoho Books

## 📋 Índice
1. [Preparación de la VM](#1-preparación-de-la-vm)
2. [Instalación de Docker](#2-instalación-de-docker)
3. [Configuración de Firewall y Puertos](#3-configuración-de-firewall-y-puertos)
4. [Configuración de Permisos](#4-configuración-de-permisos)
5. [Deployment del Proyecto](#5-deployment-del-proyecto)
6. [Pruebas y Verificación](#6-pruebas-y-verificación)
7. [Pase a Producción](#7-pase-a-producción)
8. [Monitoreo y Mantenimiento](#8-monitoreo-y-mantenimiento)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Preparación de la VM

### 1.1 Conectar a la VM
```bash
# Conectar por SSH
ssh root@TU_IP_VM
# Ingresa tu password cuando lo solicite
```

### 1.2 Actualizar Sistema
```bash
# Actualizar paquetes del sistema
apt update && apt upgrade -y

# Instalar herramientas básicas
apt install -y curl wget git nano net-tools ufw
```

### 1.3 Verificar Recursos
```bash
# Ver memoria disponible
free -h

# Ver espacio en disco
df -h

# Ver información del sistema
hostnamectl
```

**✅ Requisitos mínimos:**
- RAM: 2GB mínimo (4GB recomendado)
- Disco: 20GB libres
- CPU: 2 cores

---

## 2. Instalación de Docker

### 2.1 Instalar Docker
```bash
# Descargar script de instalación
curl -fsSL https://get.docker.com -o get-docker.sh

# Ejecutar instalación
sh get-docker.sh

# Eliminar script
rm get-docker.sh
```

### 2.2 Verificar Instalación
```bash
# Verificar versión de Docker
docker --version
# Debe mostrar: Docker version 24.x.x o superior

# Verificar Docker Compose
docker compose version
# Debe mostrar: Docker Compose version v2.x.x o superior

# Probar Docker
docker run hello-world
```

### 2.3 Configurar Docker para Auto-inicio
```bash
# Habilitar Docker al iniciar el sistema
systemctl enable docker
systemctl start docker

# Verificar estado
systemctl status docker
```

**✅ Checkpoint:** Docker debe estar instalado y corriendo.

---

## 3. Configuración de Firewall y Puertos

### 3.1 Configurar UFW (Firewall)
```bash
# Verificar estado de UFW
ufw status

# Si está inactivo, habilitarlo
ufw enable

# Permitir SSH (IMPORTANTE: hazlo primero o te bloquearás)
ufw allow 22/tcp

# Permitir puerto de la aplicación
ufw allow 8080/tcp

# Si usarás nginx después
ufw allow 80/tcp
ufw allow 443/tcp

# Recargar firewall
ufw reload

# Verificar reglas
ufw status numbered
```

**Salida esperada:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
8080/tcp                   ALLOW       Anywhere
```

### 3.2 Verificar Puertos Disponibles
```bash
# Ver qué puertos están en uso
netstat -tuln | grep LISTEN

# Verificar específicamente el puerto 8080
netstat -tuln | grep :8080
# No debe mostrar nada (puerto libre)
```

### 3.3 Test de Conectividad
```bash
# Desde tu máquina local, probar SSH
ssh root@TU_IP_VM -p 22

# Probar que el puerto 8080 esté accesible (después de desplegar)
# telnet TU_IP_VM 8080
```

**✅ Checkpoint:** Firewall configurado, puertos abiertos correctamente.

---

## 4. Configuración de Permisos

### 4.1 Crear Usuario No-Root (Recomendado para Producción)
```bash
# Crear usuario para la aplicación
adduser mcp-admin
# Sigue las instrucciones, crea una password segura

# Agregar al grupo docker
usermod -aG docker mcp-admin

# Dar privilegios sudo
usermod -aG sudo mcp-admin

# Verificar grupos
groups mcp-admin
```

### 4.2 Configurar SSH para el Nuevo Usuario
```bash
# Copiar claves SSH del root al nuevo usuario
mkdir -p /home/mcp-admin/.ssh
cp /root/.ssh/authorized_keys /home/mcp-admin/.ssh/
chown -R mcp-admin:mcp-admin /home/mcp-admin/.ssh
chmod 700 /home/mcp-admin/.ssh
chmod 600 /home/mcp-admin/.ssh/authorized_keys
```

### 4.3 Probar Nuevo Usuario
```bash
# Cambiar a nuevo usuario
su - mcp-admin

# Verificar acceso a Docker
docker ps

# Si funciona, salir
exit
```

**✅ Checkpoint:** Usuario no-root creado con permisos Docker.

---

## 5. Deployment del Proyecto

### 5.1 Crear Estructura de Directorios
```bash
# Como usuario mcp-admin (o root si prefieres)
su - mcp-admin  # Si creaste el usuario

# Crear directorio del proyecto
mkdir -p ~/zoho-mcp-server
cd ~/zoho-mcp-server

# Crear subdirectorios
mkdir -p openapi-all
mkdir -p logs
mkdir -p backups
```

### 5.2 Transferir Archivos desde tu Máquina Local

**Opción A: Usar SCP (desde tu máquina local)**
```bash
# Variables (ajusta según tu configuración)
VM_IP="TU_IP_VM"
VM_USER="mcp-admin"  # o "root"

# Transferir archivos principales
scp server.py ${VM_USER}@${VM_IP}:~/zoho-mcp-server/
scp config.py ${VM_USER}@${VM_IP}:~/zoho-mcp-server/
scp Dockerfile ${VM_USER}@${VM_IP}:~/zoho-mcp-server/
scp docker-compose.yml ${VM_USER}@${VM_IP}:~/zoho-mcp-server/
scp requirements.txt ${VM_USER}@${VM_IP}:~/zoho-mcp-server/
scp .dockerignore ${VM_USER}@${VM_IP}:~/zoho-mcp-server/

# Transferir carpeta OpenAPI
scp -r openapi-all/* ${VM_USER}@${VM_IP}:~/zoho-mcp-server/openapi-all/
```

**Opción B: Usar Git (recomendado)**
```bash
# En la VM
cd ~/zoho-mcp-server
git clone https://github.com/TU_USUARIO/TU_REPO.git .
```

### 5.3 Crear y Configurar .env
```bash
cd ~/zoho-mcp-server

# Crear archivo .env
nano .env
```

**Contenido del .env:**
```bash
ZOHO_CLIENT_ID=1000.OFMGNAJ91I937RWIREHND7BA8U0IKC
ZOHO_CLIENT_SECRET=c1317f610654292d9ed3e6cb06162c4c119fc94c80
ZOHO_REFRESH_TOKEN=1000.c4aa1f62c99d78d33c60e578a113ecbf.c8134735b7729585408df5104e217999
ZOHO_ORG_ID=REEMPLAZA_CON_TU_ORG_ID_REAL
ZOHO_BASE_URL=https://www.zohoapis.com/books/v3
```

**⚠️ IMPORTANTE:** Reemplaza `ZOHO_ORG_ID` con tu Organization ID real de Zoho.

```bash
# Guardar: Ctrl+O, Enter
# Salir: Ctrl+X

# Proteger el archivo .env
chmod 600 .env
```

### 5.4 Verificar Archivos
```bash
# Listar archivos del proyecto
ls -la ~/zoho-mcp-server/

# Verificar que estén todos los archivos necesarios:
# ✓ server.py
# ✓ config.py
# ✓ Dockerfile
# ✓ docker-compose.yml
# ✓ requirements.txt
# ✓ .env
# ✓ openapi-all/ (con archivos YAML dentro)

# Verificar archivos YAML en openapi-all
ls -la ~/zoho-mcp-server/openapi-all/
```

**✅ Checkpoint:** Todos los archivos están en la VM.

---

## 6. Pruebas y Verificación

### 6.1 Build de la Imagen Docker
```bash
cd ~/zoho-mcp-server

# Construir imagen (primera vez tarda más)
docker compose build

# Verificar que la imagen se creó
docker images | grep zoho-mcp
```

### 6.2 Levantar el Servicio (Modo Test)
```bash
# Iniciar en modo foreground para ver logs
docker compose up

# Deberías ver logs como:
# ✅ "Access token obtained"
# ✅ "Building MCP from OpenAPI spec"
# ✅ "MCP server initialized successfully"
# ✅ "Starting MCP server at http://0.0.0.0:8080"

# Si todo va bien, detener con Ctrl+C
```

### 6.3 Levantar en Modo Daemon (Background)
```bash
# Iniciar en background
docker compose up -d

# Verificar que está corriendo
docker compose ps

# Ver logs
docker compose logs -f
# Ctrl+C para salir de los logs (el servicio sigue corriendo)
```

### 6.4 Pruebas de Funcionamiento

**Test 1: Health Check Local**
```bash
# Desde la VM
curl http://localhost:8080/health

# Respuesta esperada: 200 OK o similar
```

**Test 2: Health Check Remoto**
```bash
# Desde tu máquina local
curl http://TU_IP_VM:8080/health
```

**Test 3: Verificar Logs**
```bash
# Ver últimos 50 logs
docker compose logs --tail=50

# Buscar errores
docker compose logs | grep -i error
docker compose logs | grep -i warning
```

**Test 4: Probar Endpoint de la API**
```bash
# Ejemplo: listar contactos (ajusta según tu API)
curl -X GET "http://TU_IP_VM:8080/contacts?organization_id=TU_ORG_ID" \
  -H "Content-Type: application/json"
```

### 6.5 Checklist de Verificación

```bash
# Ejecutar este script de verificación
cat << 'EOF' > ~/check_mcp.sh
#!/bin/bash
echo "🔍 Verificando Servidor MCP..."
echo "================================"

echo "✓ Contenedor corriendo:"
docker compose ps | grep Up && echo "  ✅ OK" || echo "  ❌ FALLO"

echo "✓ Health endpoint:"
curl -s http://localhost:8080/health > /dev/null && echo "  ✅ OK" || echo "  ❌ FALLO"

echo "✓ Puerto 8080 escuchando:"
netstat -tuln | grep :8080 > /dev/null && echo "  ✅ OK" || echo "  ❌ FALLO"

echo "✓ Sin errores críticos en logs:"
docker compose logs --tail=100 | grep -i "error" | grep -v "no error" && echo "  ⚠️  HAY ERRORES" || echo "  ✅ OK"

echo "================================"
echo "✅ Verificación completada"
EOF

chmod +x ~/check_mcp.sh
./check_mcp.sh
```

**✅ Checkpoint:** El servicio funciona correctamente en modo test.

---

## 7. Pase a Producción

### 7.1 Configurar Auto-restart
```bash
# El docker-compose.yml ya tiene "restart: unless-stopped"
# Verificar que esté configurado
grep restart docker-compose.yml

# Probar reinicio automático
docker compose restart
docker compose ps  # Debe volver a "Up" automáticamente
```

### 7.2 Configurar Systemd Service (Opcional pero Recomendado)
```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/zoho-mcp.service
```

**Contenido del archivo:**
```ini
[Unit]
Description=Zoho MCP Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/mcp-admin/zoho-mcp-server
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=mcp-admin
Group=mcp-admin

[Install]
WantedBy=multi-user.target
```

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio
sudo systemctl enable zoho-mcp.service

# Iniciar servicio
sudo systemctl start zoho-mcp.service

# Verificar estado
sudo systemctl status zoho-mcp.service
```

### 7.3 Configurar Logs Persistentes
```bash
cd ~/zoho-mcp-server

# Modificar docker-compose.yml para logs persistentes
nano docker-compose.yml
```

**Agregar sección de logging:**
```yaml
services:
  zoho-mcp:
    # ... configuración existente ...
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

```bash
# Aplicar cambios
docker compose down
docker compose up -d
```

### 7.4 Configurar Backups Automáticos
```bash
# Crear script de backup
nano ~/backup_mcp.sh
```

**Contenido del script:**
```bash
#!/bin/bash
BACKUP_DIR="/home/mcp-admin/zoho-mcp-server/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="mcp_backup_${TIMESTAMP}.tar.gz"

echo "🔄 Creando backup: ${BACKUP_FILE}"

# Crear backup
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    --exclude='backups' \
    --exclude='logs' \
    /home/mcp-admin/zoho-mcp-server/

# Mantener solo los últimos 7 backups
cd "${BACKUP_DIR}"
ls -t mcp_backup_*.tar.gz | tail -n +8 | xargs -r rm

echo "✅ Backup completado"
```

```bash
# Hacer ejecutable
chmod +x ~/backup_mcp.sh

# Probar backup
~/backup_mcp.sh

# Programar backup diario con cron
crontab -e

# Agregar esta línea (backup diario a las 2 AM)
0 2 * * * /home/mcp-admin/backup_mcp.sh >> /home/mcp-admin/backup_mcp.log 2>&1
```

### 7.5 Configurar Monitoreo de Salud
```bash
# Crear script de health check
nano ~/health_check.sh
```

**Contenido:**
```bash
#!/bin/bash
WEBHOOK_URL="TU_WEBHOOK_SLACK_O_DISCORD"  # Opcional

if ! curl -sf http://localhost:8080/health > /dev/null; then
    echo "❌ Servidor MCP NO responde - $(date)" | tee -a ~/health_check.log
    
    # Reintentar levantar el servicio
    cd ~/zoho-mcp-server
    docker compose restart
    
    # Opcional: Enviar alerta (descomentar si tienes webhook)
    # curl -X POST "$WEBHOOK_URL" -d '{"text":"⚠️ Servidor MCP caído, reiniciando..."}'
else
    echo "✅ Servidor MCP OK - $(date)" >> ~/health_check.log
fi
```

```bash
chmod +x ~/health_check.sh

# Programar health check cada 5 minutos
crontab -e

# Agregar:
*/5 * * * * /home/mcp-admin/health_check.sh
```

### 7.6 Hardening de Seguridad

**A) Cambiar puerto SSH (Opcional)**
```bash
sudo nano /etc/ssh/sshd_config

# Cambiar línea:
# Port 22
# por:
# Port 2222

sudo systemctl restart sshd

# Actualizar firewall
sudo ufw allow 2222/tcp
sudo ufw delete allow 22/tcp
```

**B) Configurar fail2ban**
```bash
sudo apt install fail2ban -y

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

**C) Actualizar Docker regularmente**
```bash
# Crear script de actualización
nano ~/update_mcp.sh
```

**Contenido:**
```bash
#!/bin/bash
echo "🔄 Actualizando servidor MCP..."

cd ~/zoho-mcp-server

# Backup antes de actualizar
~/backup_mcp.sh

# Pull de cambios (si usas git)
git pull origin main

# Rebuild y restart
docker compose down
docker compose build --no-cache
docker compose up -d

echo "✅ Actualización completada"
docker compose logs --tail=50
```

**✅ Checkpoint:** Servidor en producción con auto-restart, backups y monitoreo.

---

## 8. Monitoreo y Mantenimiento

### 8.1 Dashboard de Monitoreo Rápido
```bash
# Crear script de dashboard
nano ~/mcp_dashboard.sh
```

**Contenido:**
```bash
#!/bin/bash
clear
echo "═══════════════════════════════════════"
echo "   📊 DASHBOARD SERVIDOR MCP ZOHO      "
echo "═══════════════════════════════════════"
echo ""

echo "🟢 ESTADO DEL SERVICIO:"
docker compose ps
echo ""

echo "💾 USO DE RECURSOS:"
docker stats --no-stream zoho-mcp-server
echo ""

echo "🔌 CONEXIONES ACTIVAS (puerto 8080):"
netstat -an | grep :8080 | grep ESTABLISHED | wc -l
echo ""

echo "📝 ÚLTIMOS 10 LOGS:"
docker compose logs --tail=10
echo ""

echo "💿 ESPACIO EN DISCO:"
df -h / | tail -1
echo ""

echo "═══════════════════════════════════════"
```

```bash
chmod +x ~/mcp_dashboard.sh

# Ejecutar cuando necesites ver el estado
~/mcp_dashboard.sh
```

### 8.2 Comandos de Mantenimiento Diario

**Ver estado general:**
```bash
cd ~/zoho-mcp-server
docker compose ps
docker compose logs --tail=50
```

**Ver métricas en tiempo real:**
```bash
docker stats zoho-mcp-server
```

**Limpiar logs antiguos:**
```bash
docker compose logs --tail=0 > /dev/null 2>&1
```

**Reiniciar servicio:**
```bash
docker compose restart
```

**Ver errores recientes:**
```bash
docker compose logs --tail=100 | grep -i error
```

### 8.3 Rotación de Logs
```bash
# Crear archivo de configuración logrotate
sudo nano /etc/logrotate.d/docker-compose
```

**Contenido:**
```
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  size=10M
  missingok
  delaycompress
  copytruncate
}
```

**✅ Checkpoint:** Monitoreo configurado y funcionando.

---

## 9. Troubleshooting

### Problema 1: Contenedor no inicia
```bash
# Ver logs detallados
docker compose logs

# Ver logs del sistema
journalctl -xe

# Verificar configuración
docker compose config

# Rebuild completo
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### Problema 2: Error de autenticación con Zoho
```bash
# Verificar variables de entorno
docker compose exec zoho-mcp env | grep ZOHO

# Probar token manualmente
curl -X POST "https://accounts.zoho.com/oauth/v2/token" \
  -d "refresh_token=TU_REFRESH_TOKEN" \
  -d "client_id=TU_CLIENT_ID" \
  -d "client_secret=TU_CLIENT_SECRET" \
  -d "grant_type=refresh_token"
```

### Problema 3: Puerto 8080 no responde
```bash
# Verificar que el puerto esté escuchando
netstat -tuln | grep :8080

# Verificar firewall
ufw status | grep 8080

# Verificar desde fuera
# (en tu máquina local)
telnet TU_IP_VM 8080

# Si falla, revisar firewall del proveedor cloud (AWS, GCP, etc.)
```

### Problema 4: Contenedor se reinicia constantemente
```bash
# Ver por qué está fallando
docker compose logs --tail=100

# Ver eventos del contenedor
docker events --filter 'container=zoho-mcp-server'

# Entrar al contenedor para debug
docker compose exec zoho-mcp bash
```

### Problema 5: Memoria insuficiente
```bash
# Ver uso de memoria
free -h

# Ver uso por contenedor
docker stats

# Agregar swap si es necesario
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Problema 6: Archivos OpenAPI no encontrados
```bash
# Verificar que existan
ls -la ~/zoho-mcp-server/openapi-all/

# Si están vacíos, transferir nuevamente
# (desde tu máquina local)
scp -r openapi-all/* mcp-admin@TU_IP_VM:~/zoho-mcp-server/openapi-all/
```

---

## 📚 Comandos de Referencia Rápida

### Gestión del Servicio
```bash
# Iniciar
docker compose up -d

# Detener
docker compose down

# Reiniciar
docker compose restart

# Ver logs
docker compose logs -f

# Ver estado
docker compose ps

# Rebuild
docker compose up -d --build
```

### Monitoreo
```bash
# Dashboard
~/mcp_dashboard.sh

# Logs en vivo
docker compose logs -f --tail=100

# Verificar salud
curl http://localhost:8080/health

# Uso de recursos
docker stats
```

### Mantenimiento
```bash
# Backup manual
~/backup_mcp.sh

# Actualizar
~/update_mcp.sh

# Verificar sistema
~/check_mcp.sh

# Limpiar Docker
docker system prune -a
```

---

## ✅ Checklist Final de Producción

- [ ] Docker instalado y corriendo
- [ ] Firewall configurado (puertos 22, 8080)
- [ ] Usuario no-root creado (mcp-admin)
- [ ] Proyecto desplegado en ~/zoho-mcp-server
- [ ] Archivo .env configurado con credenciales reales
- [ ] Archivos OpenAPI en openapi-all/
- [ ] Servicio levantado con docker-compose
- [ ] Health check responde correctamente
- [ ] Servicio systemd configurado
- [ ] Backups automáticos configurados
- [ ] Monitoreo de salud configurado (cron)
- [ ] Logs rotativos configurados
- [ ] Dashboard de monitoreo funcional
- [ ] Documentación de troubleshooting revisada

---

## 🎯 Próximos Pasos (Opcional)

1. **Implementar Nginx con SSL** (usar docker-compose-con-nginx.yml)
2. **Configurar dominio personalizado**
3. **Implementar rate limiting**
4. **Configurar alertas (Slack/Discord/Email)**
5. **Implementar CI/CD con GitHub Actions**
6. **Configurar monitoreo con Prometheus + Grafana**

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker compose logs`
2. Ejecuta el script de verificación: `~/check_mcp.sh`
3. Consulta la sección de Troubleshooting
4. Revisa los issues en el repositorio del proyecto

---

**¡Tu servidor MCP está listo para producción! 🚀**
