# SERFOR API - Natural Language Query Service

API backend con FastAPI que procesa consultas en lenguaje natural sobre datos de SERFOR usando agentes de IA.

## Requisitos Previos

- Python 3.11 o superior
- [uv](https://docs.astral.sh/uv/) - Gestor de paquetes y entornos virtuales de Python
- Credenciales para SQL Server (ver README principal)
- ODBC Driver 18 for SQL Server instalado en tu sistema

### Instalar uv

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Importante: Recargar el PATH para poder usar el comando 'uv' inmediatamente
source $HOME/.local/bin/env
```

### Instalar ODBC Driver 18 for SQL Server

**Windows:**
Descarga desde: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

**macOS:**
```bash
brew install msodbcsql18
```

**Linux (Ubuntu/Debian):**
```bash
# Añadir repositorio de Microsoft
sudo curl https://packages.microsoft.com/config/rhel/9/prod.repo | sudo tee /etc/yum.repos.d/mssql-release.repo

# Eliminar conflictos de paquetes si existen
sudo yum remove unixODBC-utf16 unixODBC-utf16-devel

# Instalar driver (Aceptar EULA automáticamente)
sudo ACCEPT_EULA=Y yum install -y msodbcsql18
```

## Instalación

1. Navega a la carpeta del API:
```bash
cd api
```

2. **Opción A: Usando UV (recomendado para desarrollo local)**

Crea el entorno virtual e instala las dependencias con uv:
```bash
uv sync
```

Esto creará automáticamente un entorno virtual en `.venv/` e instalará todas las dependencias del `pyproject.toml`.

**Opción B: Usando pip (para repositorios remotos)**

```bash
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env` en la carpeta `api/` con las siguientes variables:

```env
# Database Configuration (SQL Server)
DB_SERVER=your_server_here
DB_PORT=1433
DB_DATABASE=your_database_here
DB_USERNAME=your_username_here
DB_PASSWORD=your_password_here
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUST_CERT=yes

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# CORS Configuration (separar multiples origenes con coma)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Auth Dev Mode (solo para desarrollo local)
AUTH_DEV_MODE=false
AUTH_DEV_USER=dev_user
AUTH_DEV_PASSWORD=dev123

# JWT Configuration (generar secret seguro para produccion)
JWT_SECRET=your_jwt_secret_here

# SGI Seguridad Configuration
SGI_BASE_URL=https://sgi-base-url
SGI_SISTEMA_ID=41
SGI_COMPAGNIA_ID=1

```

## Encriptación de Variables de Entorno (QA/Producción)

En ambientes de QA y Producción, el archivo `.env` debe estar **encriptado** para proteger credenciales sensibles. El sistema usa encriptación AES (Fernet) con una clave que se configura como variable de entorno del servidor.

### Flujo de trabajo

```
┌─────────────────┐     encriptar      ┌──────────────────┐
│  .env           │ ─────────────────► │  .env.encrypted  │
│  (texto plano)  │                    │  (seguro)        │
│  LOCAL ONLY     │                    │  COMMIT OK       │
└─────────────────┘                    └──────────────────┘
                                                │
                                                ▼ deploy
                                       ┌──────────────────┐
                                       │  Servidor QA/Prod│
                                       │  ENV_ENCRYPTION_ │
                                       │  KEY=xxx         │
                                       └──────────────────┘
```

### Comandos disponibles

```bash
# Generar una nueva clave de encriptación
uv run python scripts/env_encrypt.py generate-key

# Encriptar el archivo .env
uv run python scripts/env_encrypt.py encrypt --key "TU_CLAVE_SECRETA"

# Verificar que se puede desencriptar (muestra contenido)
uv run python scripts/env_encrypt.py decrypt --key "TU_CLAVE_SECRETA"

# Desencriptar a un archivo (opcional, para debug)
uv run python scripts/env_encrypt.py decrypt --key "TU_CLAVE_SECRETA" --output .env.decrypted
```

### Proceso para actualizar variables de entorno

1. **Modificar** el archivo `.env` local con los nuevos valores

2. **Encriptar** el archivo:
   ```bash
   uv run python scripts/env_encrypt.py encrypt --key "CLAVE_DEL_PROYECTO"
   ```

3. **Commitear** el archivo `.env.encrypted` (es seguro, está encriptado)

4. **Desplegar** a QA/Producción

> **IMPORTANTE:** 
- La clave de encriptación (`CLAVE_DEL_PROYECTO`) debe ser la misma que está configurada en el servidor. Si generas una nueva clave, deberás actualizarla también en el servidor.

### Configuración en el servidor (QA/Producción)

1. **Configurar la variable de entorno** `ENV_ENCRYPTION_KEY`:

   **Opción A: En systemd (recomendado)**
   ```ini
   # /etc/systemd/system/serfor-api.service
   [Service]
   Environment="ENV_ENCRYPTION_KEY=tu_clave_secreta_aqui"
   ExecStart=/path/to/uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

   **Opción B: En el shell/profile**
   ```bash
   export ENV_ENCRYPTION_KEY="tu_clave_secreta_aqui"
   ```

2. **Eliminar** cualquier archivo `.env` en texto plano del servidor (si existe)

3. **Verificar** que solo exista `.env.encrypted`

4. **Reiniciar** el servicio:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart iadir_back
   ```

### Validar en local (simular producción)

```bash
# Renombrar .env para que no lo use
mv .env .env.backup

# Levantar con la clave de encriptación
ENV_ENCRYPTION_KEY="TU_CLAVE" uv run uvicorn app.main:app --reload

# Restaurar cuando termines
mv .env.backup .env
```

### Notas de seguridad

- **NUNCA** commitear el archivo `.env` en texto plano
- **NUNCA** commitear la clave de encriptación en el código
- El archivo `.env.encrypted` **SÍ** es seguro para commitear
- La clave debe guardarse en un **gestor de contraseñas** o **secrets manager**
- Si sospechas que la clave fue comprometida, genera una nueva y re-encripta

## Ejecución

```bash
# Activar entorno virtual manualmente
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows
```

### Modo Desarrollo

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O usando el script de inicio:

```bash
uv run python run.py
```

### Modo Producción

Consultar documentación de despliegue.

## Verificación

Una vez iniciado el servidor, accede a:

- **API Docs (Swagger):** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Estructura del Proyecto

```
api/
├── app/
│   ├── core/          # Configuración y settings
│   ├── models/        # Modelos Pydantic
│   ├── routes/        # Endpoints de la API
│   ├── services/      # Lógica de negocio y orquestación
│   └── main.py        # Punto de entrada de FastAPI
├── agents/            # Agentes de IA (orchestrator, planner, executor, etc.)
├── database/          # Gestión de conexiones y esquemas de BD
├── utils/             # Utilidades (logger, debug tools)
├── pyproject.toml     # Configuración del proyecto y dependencias (UV)
├── requirements.txt   # Dependencias para pip (compatibilidad)
├── uv.lock            # Lock file de UV
├── .python-version    # Versión de Python requerida
├── run.py             # Script de inicio
└── README.md          # Esta documentación
```

## Comandos Útiles

```bash
# Activar entorno virtual manualmente
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows

# Agregar nueva dependencia
uv add nombre-paquete

# Actualizar dependencias
uv sync --upgrade

# Ver dependencias instaladas
uv pip list
```
