# Guía Rápida: Configuración Zoho Books OAuth

## 1. Crear Cliente OAuth en Zoho Console

1. Ve a: https://api-console.zoho.com/
2. Click en **"ADD CLIENT"**
3. Selecciona **"Server-based Applications"** (NO Client-based)
4. Llena los campos:
   ```
   Client Name: Zoho Books MCP Server
   Homepage URL: http://localhost:8080
   Authorized Redirect URIs: http://localhost:8080/oauth/callback
   ```
5. Click **"CREATE"**
6. **Copia y guarda:**
   - `Client ID`
   - `Client Secret`

---

## 2. Obtener Refresh Token

### 2.1 Generar Authorization Code

Abre en el navegador (reemplaza `YOUR_CLIENT_ID` con tu Client ID real):

```
https://accounts.zoho.com/oauth/v2/auth?scope=ZohoBooks.fullaccess.all&client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost:8080/oauth/callback&access_type=offline
```

**⚠️ Ajusta el dominio según tu región:**
- 🇺🇸 US: `accounts.zoho.com`
- 🇪🇺 EU: `accounts.zoho.eu`
- 🇮🇳 IN: `accounts.zoho.in`
- 🇦🇺 AU: `accounts.zoho.com.au`

Te redirige a:
```
http://localhost:8080/oauth/callback?code=1000.abc123...&location=us
```

**⏱️ IMPORTANTE: El `code` expira en 60 segundos. Cópialo inmediatamente.**

### 2.2 Intercambiar por Refresh Token (en menos de 60s)

Ten este comando listo en tu terminal. Solo pega el `code` nuevo y ejecuta rápido:

```bash
curl -X POST https://accounts.zoho.com/oauth/v2/token \
  -d "code=PEGA_EL_CODE_AQUI" \
  -d "client_id=TU_CLIENT_ID" \
  -d "client_secret=TU_CLIENT_SECRET" \
  -d "redirect_uri=http://localhost:8080/oauth/callback" \
  -d "grant_type=authorization_code"
```

**Response exitoso:**
```json
{
  "access_token": "1000.7fe0e6...",
  "refresh_token": "1000.c4eac4...",  // ← Guarda este
  "expires_in": 3600
}
```

**Si ves `{"error":"invalid_code"}`** → El code expiró, repite paso 2.1

---

## 3. Obtener Organization ID

**El Organization ID está en la URL de Zoho Books:**

1. Ve a: https://books.zoho.com
2. Inicia sesión (si es cuenta nueva, crea una organización primero)
3. Observa la URL en el dashboard:
   ```
   https://books.zoho.com/app/906765370#/dashboard
                            ^^^^^^^^^ 
                            Este es tu Organization ID
   ```

O también puede aparecer así:
```
https://books.zoho.com/app#/dashboard/906765370
```

**Copia ese número, es tu `ZOHO_ORGANIZATION_ID`.**

---

## 4. Configurar archivo .env

Crea o edita el archivo `.env` en la raíz del proyecto:

```bash
# En la raíz del proyecto
nano .env
```

Pega esta configuración (reemplaza con tus valores reales):

```bash
ZOHO_CLIENT_ID=1000.XOVKY9XAFOTDC4DUU0JUZH2GC3VNOT
ZOHO_CLIENT_SECRET=c2f7ae33bf9b83e584bd261fa62ecdcc77f2d6a6b4
ZOHO_REFRESH_TOKEN=1000.c4eac4730aea3cf8a8fe13cc048f472a.1cd80029463c35ff6094dc7dd1694034
ZOHO_ORGANIZATION_ID=906765370
ZOHO_REGION=com
ZOHO_API_BASE_URL=https://www.zohoapis.com/books/v3
```

**Regiones disponibles:**
- US: `com` → `https://www.zohoapis.com`
- EU: `eu` → `https://www.zohoapis.eu`
- IN: `in` → `https://www.zohoapis.in`
- AU: `com.au` → `https://www.zohoapis.com.au`

Guarda el archivo (Ctrl+O, Enter, Ctrl+X en nano).

---

## 5. Verificar configuración

```bash
# Ver que todas las variables estén configuradas
cat .env

# Reiniciar el servidor MCP
lsof -ti:8080 | xargs kill -9
python server.py
```

---

## 6. Probar conexión

En Claude, ejecuta:

```
Create a simple contact in Zoho Books with name "Test Contact"
```

Si todo está bien, debería crear el contacto exitosamente. ✅

---

## Troubleshooting

| Error | Causa | Solución |
|-------|-------|----------|
| `{"error":"invalid_code"}` | Code expiró (>60s) | Repite paso 2.1 y ejecuta curl rápido |
| `"organizations": []` | No hay org creada | Crea organización en books.zoho.com |
| `103001: Trial expirado` | Cuenta sin plan activo | Activa plan de pago en Zoho Books |
| `401 Unauthorized` | Refresh token inválido | Repite pasos 2.1 y 2.2 |
| `1038: JSON not well formed` | Formato JSON incorrecto | Verificar que src/zoho_client.py envíe JSON directo |

---

## Notas Importantes

- ⏱️ El `code` expira en **60 segundos**
- 🔄 El `refresh_token` **nunca expira** (úsalo siempre)
- 🔑 Nunca compartas tu `.env` en Git (agrégalo a `.gitignore`)
- 💳 Necesitas cuenta con **plan activo** (no trial expirado)
- 🌍 Usa el dominio API correcto según tu región

---

## Arquitectura del Proyecto

```
rava-crm-zoho/
├── .env                    # Variables de entorno (NO subir a Git)
├── server.py               # Servidor MCP principal
├── config.py               # Configuración de Zoho
└── src/
    ├── constants.py        # Lista de herramientas permitidas
    ├── zoho_client.py      # Cliente HTTP personalizado (JSON directo)
    └── openapi_utils.py    # Generación de schemas dinámicos
```

---

## Ejemplo de uso en Claude

```python
# Crear contacto
create_contact(
    contact_name="Tech Solutions LATAM",
    company_name="Tech Solutions S.A.",
    contact_type="customer",
    contact_persons=[{
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan@techsolutions.com",
        "phone": "+57 300 1234567"
    }],
    billing_address={
        "address": "Calle 100 #15-20",
        "city": "Bogotá",
        "state": "Cundinamarca",
        "zip": "110111",
        "country": "Colombia"
    }
)

# Listar contactos
list_contacts(contact_type="customer", per_page=50)

# Crear factura
create_invoice(
    customer_id="123456",
    line_items=[{
        "item_id": "789",
        "quantity": 2,
        "rate": 100.00
    }]
)
```

---

## Referencias

- **Zoho Books API Docs**: https://www.zoho.com/books/api/v3/
- **Zoho OAuth Guide**: https://www.zoho.com/accounts/protocol/oauth/web-server-applications.html
- **API Console**: https://api-console.zoho.com/
