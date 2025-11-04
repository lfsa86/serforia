# SERFOR - Sistema de Consultas con Lenguaje Natural

Sistema de consultas en lenguaje natural para datos de SERFOR, utilizando agentes de IA para procesar y visualizar información forestal.

## Arquitectura del Proyecto

El proyecto está organizado en tres componentes principales:

```
naturai-serfor-demo/
├── api/                  # Backend FastAPI (Python con uv)
├── client/               # Frontend React (Node.js)
├── init/                 # Scripts SQL de inicialización
│   ├── setup.sql         # Crea DB y schema
│   ├── DataPilotoIA.sql  # Crea tablas y datos
│   └── entrypoint.sh     # Script de inicialización automática
├── Dockerfile            # SQL Server con auto-setup
├── build-and-run.bat     # Script Windows para DB
├── build-and-run.sh      # Script Linux/Mac para DB
├── streamlit_app.py      # Aplicación Streamlit (disponible, no en Docker)
└── README.md             # Esta documentación
```

### Componentes

1. **API Backend** - FastAPI + Python
   - Procesamiento de consultas en lenguaje natural
   - Agentes de IA con InstantNeo y OpenAI
   - Conexión a SQL Server para datos de SERFOR
   - Gestión con **uv** (entorno virtual)

2. **Client Frontend** - React + TypeScript + Vite
   - Interfaz web interactiva
   - Comunicación con API via REST
   - Visualización de resultados

3. **SQL Server** - Base de datos (Docker)
   - Contenedor con inicialización automática
   - Datos de SERFOR (SERFOR_BDDWH)
   - Scripts SQL se ejecutan automáticamente al iniciar

4. **Streamlit App** - Aplicación de visualización
   - Disponible para pruebas locales
   - No se ejecuta en Docker

## Requisitos del Sistema

- **Python 3.11+** - Para la API
- **Node.js 18+** - Para el frontend
- **Docker & Docker Compose** - Para SQL Server
- **uv** - Gestor de paquetes Python
- **ODBC Driver 18 for SQL Server** - Para conexión a BD
- **OpenAI API Key** - Para los agentes de IA

## Inicio Rápido

### 1. Instalar Dependencias Globales

**uv (Python package manager):**
```bash
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**ODBC Driver 18:**
- Windows: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- macOS: `brew install msodbcsql18`
- Linux: Ver instrucciones en [api/README.md](api/README.md)

### 2. Iniciar SQL Server

El proyecto usa un Dockerfile que automáticamente configura SQL Server y ejecuta todos los scripts de inicialización.

**En Windows:**
```bash
build-and-run.bat
```

**En Linux/Mac:**
```bash
chmod +x build-and-run.sh
./build-and-run.sh
```

**O manualmente:**
```bash
# Construir imagen
docker build -t serfor-sqlserver:latest .

# Ejecutar contenedor
docker run -d --name serfor-sqlserver -p 1433:1433 -v sqlserver_data:/var/opt/mssql serfor-sqlserver:latest

# Ver logs de inicialización
docker logs -f serfor-sqlserver
```

El contenedor automáticamente:
- ✅ Inicia SQL Server
- ✅ Espera a que esté listo
- ✅ Ejecuta `setup.sql` (crea DB y schema Dir)
- ✅ Ejecuta `DataPilotoIA.sql` (crea tablas y datos)

**Credenciales de conexión:**
- Host: `localhost,1433`
- Usuario: `sa`
- Password: `SerforDB@2025`
- Base de datos: `SERFOR_BDDWH`

Espera a que la inicialización complete (revisa los logs, toma ~30-60 segundos).

### 3. Configurar y Ejecutar API

```bash
cd api

# Crear entorno virtual e instalar dependencias
uv sync

# Crear archivo .env
echo "DB_PASSWORD=SerforDB@2025" > .env
echo "OPENAI_API_KEY=tu_api_key_aqui" >> .env

# Ejecutar API
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Ver documentación completa: [api/README.md](api/README.md)

### 4. Configurar y Ejecutar Client

```bash
cd client

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

Ver documentación completa: [client/README.md](client/README.md)

### 5. Acceder a las Aplicaciones

- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **SQL Server:** localhost:1433

## Configuración de Variables de Entorno

### API (.env en carpeta api/)

```env
# Database
DB_SERVER=localhost
DB_PORT=1433
DB_DATABASE=SERFOR_BDDWH
DB_USERNAME=sa
DB_PASSWORD=SerforDB@2025
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUST_CERT=yes

# OpenAI
OPENAI_API_KEY=tu_api_key_aqui

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Client (.env en carpeta client/)

```env
VITE_API_URL=http://localhost:8000/api
```

## Estructura del Proyecto

```
naturai-serfor-demo/
│
├── api/                          # Backend API
│   ├── app/
│   │   ├── core/                 # Configuración
│   │   ├── models/               # Modelos Pydantic
│   │   ├── routes/               # Endpoints
│   │   ├── services/             # Lógica de negocio
│   │   └── main.py               # App FastAPI
│   ├── pyproject.toml            # Dependencias (uv)
│   ├── .python-version           # Versión Python
│   └── README.md
│
├── client/                       # Frontend React
│   ├── src/
│   │   ├── components/           # Componentes UI
│   │   ├── services/             # Servicios API
│   │   └── App.tsx
│   ├── package.json              # Dependencias npm
│   └── README.md
│
├── agents/                       # Agentes de IA
│   ├── basic_agent.py
│   ├── routing_agent.py
│   ├── sql_agent.py
│   └── visualization_agent.py
│
├── database/                     # Scripts y utilidades de BD
├── utils/                        # Utilidades compartidas
├── init/                         # Scripts SQL de inicialización
│
├── init/                         # Scripts SQL inicialización
│   ├── setup.sql                 # Crea DB y schema
│   ├── DataPilotoIA.sql          # Crea tablas
│   └── entrypoint.sh             # Auto-setup script
│
├── streamlit_app.py              # App Streamlit (opcional)
├── Dockerfile                    # SQL Server con auto-setup
├── build-and-run.bat             # Windows DB setup
├── build-and-run.sh              # Linux/Mac DB setup
├── .gitignore
└── README.md                     # Esta documentación
```

## Uso de Streamlit (Opcional)

La aplicación Streamlit está disponible pero no se ejecuta en Docker:

```bash
# Desde la raíz del proyecto
# Crear entorno virtual si no existe
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export OPENAI_API_KEY=tu_api_key_aqui
export DB_SERVER=localhost
export DB_PASSWORD=SerforDB@2025

# Ejecutar Streamlit
streamlit run streamlit_app.py
```

Accede en: http://localhost:8501

## Comandos Útiles

### Docker (SQL Server)

```bash
# Construir y ejecutar (recomendado)
build-and-run.bat        # Windows
./build-and-run.sh       # Linux/Mac

# Ver logs
docker logs -f serfor-sqlserver

# Detener
docker stop serfor-sqlserver

# Eliminar contenedor
docker rm serfor-sqlserver

# Eliminar volumen (reset completo de DB)
docker volume rm sqlserver_data
```

### API

```bash
cd api

# Instalar/actualizar dependencias
uv sync

# Ejecutar en desarrollo
uv run uvicorn app.main:app --reload

# Ejecutar tests
uv run pytest

# Ver dependencias
uv pip list
```

### Client

```bash
cd client

# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Build producción
npm run build

# Preview build
npm run preview
```

## Troubleshooting

### SQL Server no inicia o scripts no se ejecutan
```bash
# Verificar logs de inicialización
docker logs -f serfor-sqlserver

# Reconstruir desde cero
docker stop serfor-sqlserver
docker rm serfor-sqlserver
docker volume rm sqlserver_data
./build-and-run.bat  # o ./build-and-run.sh

# Verificar que los scripts SQL existen
ls init/setup.sql
ls init/DataPilotoIA.sql
ls init/entrypoint.sh
```

### Error de conexión API → SQL Server
- Verifica que SQL Server esté corriendo: `docker ps`
- Confirma las credenciales en `.env`
- Verifica ODBC Driver: `odbcinst -q -d` (Linux/Mac)

### Frontend no conecta con API
- Verifica que la API esté corriendo en puerto 8000
- Revisa configuración CORS en API
- Confirma `VITE_API_URL` en `.env` del client

### Puertos ocupados
```bash
# Verificar uso de puertos
netstat -ano | findstr :8000    # Windows (API)
netstat -ano | findstr :5173    # Windows (Client)
netstat -ano | findstr :1433    # Windows (SQL Server)

lsof -ti:8000                   # macOS/Linux
```

## Testing

### API
```bash
cd api
uv run pytest
```

### Client
```bash
cd client
npm run test
```

## Deployment

Ver documentación específica en:
- [api/README.md](api/README.md) - Deployment del backend
- [client/README.md](client/README.md) - Deployment del frontend

## Contribución

1. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
2. Realiza tus cambios
3. Ejecuta tests: `cd api && uv run pytest`
4. Commit: `git commit -m "Descripción del cambio"`
5. Push: `git push origin feature/nueva-funcionalidad`
6. Crea un Pull Request

## Licencia

[Especificar licencia del proyecto]

## Contacto

[Información de contacto del equipo]
