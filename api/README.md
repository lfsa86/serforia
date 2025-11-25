# SERFOR API - Natural Language Query Service

API backend con FastAPI que procesa consultas en lenguaje natural sobre datos de SERFOR usando agentes de IA.

## Requisitos Previos

- Python 3.11 o superior
- [uv](https://docs.astral.sh/uv/) - Gestor de paquetes y entornos virtuales de Python
- SQL Server corriendo en Docker (ver README principal)
- ODBC Driver 18 for SQL Server instalado en tu sistema

### Instalar uv

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
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
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
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

1. Crea un archivo `.env` en la carpeta `api/` con las siguientes variables:

```env
# Database Configuration
DB_SERVER=localhost
DB_PORT=1433
DB_DATABASE=SERFOR_BDDWH
DB_USERNAME=sa
DB_PASSWORD=SerforDB@2025
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUST_CERT=yes

# OpenAI Configuration
OPENAI_API_KEY=tu_api_key_aqui

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost,http://localhost:80,http://localhost:5173
```

2. Asegúrate de que SQL Server esté corriendo:
```bash
# Desde la raíz del proyecto
docker-compose up -d
```

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

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Verificación

Una vez iniciado el servidor, accede a:

- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc
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

## Testing

```bash
uv run pytest
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

## Troubleshooting

### Error de conexión a SQL Server
- Verifica que el contenedor de SQL Server esté corriendo: `docker ps`
- Confirma que el puerto 1433 esté disponible
- Revisa las credenciales en el archivo `.env`

### Error con ODBC Driver
- Verifica que el driver ODBC 18 esté instalado correctamente
- En Windows, verifica en "ODBC Data Sources (64-bit)"
- En Linux/Mac, ejecuta: `odbcinst -q -d`

### Puerto 8000 en uso
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```
