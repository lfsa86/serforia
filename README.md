# SERFOR - Sistema de Consultas con Lenguaje Natural

Sistema de consultas en lenguaje natural para datos de SERFOR, utilizando agentes de IA para procesar y visualizar información forestal.

## Arquitectura del Proyecto

El proyecto está organizado en **cuatro componentes independientes**:

```
naturai-serfor-demo/
├── api/                  # Backend FastAPI (servicio independiente)
├── client/               # Frontend React (servicio independiente)
├── demo-version/         # Versión demo con Streamlit
└── demo-db/              # Base de datos SQL Server dockerizada
```

### Componentes

1. **API Backend** (`/api`) - FastAPI + Python
   - Procesamiento de consultas en lenguaje natural
   - Agentes de IA con InstantNeo y OpenAI
   - Sistema autocontenido con sus propios `agents/`, `database/`, `utils/`
   - Gestión con **uv** para desarrollo local y **pip** para repos remotos
   - Ver documentación completa: [api/README.md](api/README.md)

2. **Client Frontend** (`/client`) - React + TypeScript + Vite
   - Interfaz web interactiva moderna
   - Comunicación con API via REST
   - Visualización de resultados y gráficos
   - Completamente independiente y listo para deployment
   - Ver documentación completa: [client/README.md](client/README.md)

3. **Demo Version** (`/demo-version`) - Aplicación Streamlit
   - Versión demo del sistema con interfaz Streamlit
   - Incluye agentes, database y utils propios
   - Para pruebas y demostraciones rápidas
   - Ver documentación: [demo-version/README-streamlit.md](demo-version/README-streamlit.md)

4. **Demo DB** (`/demo-db`) - SQL Server Dockerizado
   - Contenedor Docker con SQL Server 2022
   - Inicialización automática con scripts SQL
   - Base de datos SERFOR_BDDWH lista para usar
   - Ver documentación: [demo-db/README-Docker.md](demo-db/README-Docker.md)

## Requisitos del Sistema

- **Python 3.11+** - Para API y demo-version
- **Node.js 18+** - Para el frontend
- **Docker** - Para la base de datos
- **uv** - Gestor de paquetes Python (opcional, recomendado para desarrollo)
- **ODBC Driver 18 for SQL Server** - Para conexión a BD
- **OpenAI API Key** - Para los agentes de IA

## Inicio Rápido

### Opción 1: API + Client (Arquitectura de Microservicios)

#### 1. Iniciar Base de Datos

```bash
cd demo-db

# Windows
build-and-run.bat

# Linux/Mac
chmod +x build-and-run.sh
./build-and-run.sh
```

Espera ~30-60 segundos para que la BD inicialice.

**Credenciales:**
- Host: `localhost:1433`
- Usuario: `sa`
- Password: `SerforDB@2025`
- Base de datos: `SERFOR_BDDWH`

#### 2. Configurar y Ejecutar API

```bash
cd api

# Con UV (recomendado para desarrollo local)
uv sync
echo "OPENAI_API_KEY=tu_api_key_aqui" > .env
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# O con pip
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Ver [api/README.md](api/README.md) para más detalles.

#### 3. Configurar y Ejecutar Client

```bash
cd client

npm install
npm run dev
```

Ver [client/README.md](client/README.md) para más detalles.

#### 4. Acceder a las Aplicaciones

- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

---

### Opción 2: Demo con Streamlit

#### 1. Iniciar Base de Datos

```bash
cd demo-db
./build-and-run.sh  # o build-and-run.bat en Windows
```

#### 2. Ejecutar Demo Streamlit

```bash
cd demo-version

# Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

# Ejecutar Streamlit
streamlit run streamlit_app.py
```

Ver [demo-version/README-streamlit.md](demo-version/README-streamlit.md) para más detalles.

---

## Estructura Detallada del Proyecto

```
naturai-serfor-demo/
│
├── api/                          # 🔧 Backend API (autocontenido)
│   ├── agents/                   # Agentes de IA
│   ├── database/                 # Gestión de BD y schemas
│   ├── utils/                    # Utilidades (logger, debug)
│   ├── app/
│   │   ├── core/                 # Configuración
│   │   ├── models/               # Modelos Pydantic
│   │   ├── routes/               # Endpoints
│   │   └── services/             # Lógica de negocio
│   ├── pyproject.toml            # Dependencias UV
│   ├── requirements.txt          # Dependencias pip
│   └── README.md
│
├── client/                       # 🎨 Frontend React (autocontenido)
│   ├── src/
│   │   ├── components/           # Componentes UI
│   │   ├── services/             # Cliente API
│   │   ├── types/                # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   └── README.md
│
├── demo-version/                 # 🚀 Demo Streamlit
│   ├── agents/                   # Agentes de IA
│   ├── database/                 # Gestión de BD
│   ├── utils/                    # Utilidades
│   ├── logs/                     # Logs de la demo
│   ├── streamlit_app.py          # App principal
│   ├── run_streamlit.py          # Script de ejecución
│   ├── requirements.txt          # Dependencias
│   ├── .env.example              # Plantilla de configuración
│   ├── README-streamlit.md       # Documentación Streamlit
│   └── README-Agents.md          # Documentación de agentes
│
├── demo-db/                      # 🗄️ Base de Datos Docker
│   ├── init/                     # Scripts SQL (138MB)
│   │   ├── setup.sql
│   │   ├── DataPilotoIA.sql
│   │   ├── scriptBDIA29102025.sql
│   │   ├── PATCH_correccion_vistas.sql
│   │   └── entrypoint.sh
│   ├── Dockerfile                # SQL Server 2022
│   ├── build-and-run.sh          # Script Linux/Mac
│   ├── build-and-run.bat         # Script Windows
│   ├── setup_database.py         # Setup y enrichment
│   └── README-Docker.md          # Documentación Docker
│
├── .gitignore
└── README.md                     # Esta documentación
```

## Configuración de Variables de Entorno

### API (`api/.env`)

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

### Client (`client/.env`)

```env
VITE_API_URL=http://localhost:8000/api
```

### Demo Version (`demo-version/.env`)

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
```

## Comandos Útiles

### Base de Datos (demo-db)

```bash
cd demo-db

# Construir y ejecutar
./build-and-run.sh              # Linux/Mac
build-and-run.bat               # Windows

# Ver logs
docker logs -f serfor-sqlserver

# Detener
docker stop serfor-sqlserver

# Eliminar y reconstruir
docker stop serfor-sqlserver
docker rm serfor-sqlserver
docker volume rm sqlserver_data
./build-and-run.sh
```

### API

```bash
cd api

# Con UV
uv sync                          # Instalar/actualizar deps
uv run uvicorn app.main:app --reload
uv run pytest                    # Tests

# Con pip
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

### Client

```bash
cd client

npm install                      # Instalar dependencias
npm run dev                      # Desarrollo
npm run build                    # Build producción
npm run preview                  # Preview build
npm run lint                     # Linting
```

### Demo Streamlit

```bash
cd demo-version

pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Troubleshooting

### Base de Datos

**SQL Server no inicia:**
```bash
docker logs -f serfor-sqlserver  # Ver logs de error
docker ps                        # Verificar que esté corriendo
```

**Reconstruir desde cero:**
```bash
cd demo-db
docker stop serfor-sqlserver
docker rm serfor-sqlserver
docker volume rm sqlserver_data
./build-and-run.sh
```

### API

**Error de conexión a BD:**
- Verifica que SQL Server esté corriendo: `docker ps`
- Confirma credenciales en `api/.env`
- Verifica ODBC Driver: `odbcinst -q -d` (Linux/Mac)

**Puerto 8000 ocupado:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Client

**Frontend no conecta con API:**
- Verifica que API esté corriendo en http://localhost:8000
- Revisa `VITE_API_URL` en `client/.env`
- Confirma CORS en `api/.env`

**Puerto 5173 ocupado:**
```bash
npm run dev -- --port 3000       # Usar puerto diferente
```

## Testing

### API
```bash
cd api
uv run pytest                    # Con UV
pytest                           # Con pip
```

### Client
```bash
cd client
npm run test
```

## Deployment

Cada servicio es independiente y puede ser desplegado por separado:

- **API**: Ver [api/README.md](api/README.md) - Despliegue con Docker, Railway, Render, etc.
- **Client**: Ver [client/README.md](client/README.md) - Despliegue en Vercel, Netlify, etc.
- **Base de Datos**: Ver [demo-db/README-Docker.md](demo-db/README-Docker.md) - SQL Server en Docker

## Contribución

1. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
2. Realiza cambios en el servicio correspondiente (`api/`, `client/`, etc.)
3. Ejecuta tests del servicio
4. Commit: `git commit -m "feat: descripción del cambio"`
5. Push: `git push origin feature/nueva-funcionalidad`
6. Crea un Pull Request

## Documentación Adicional

- [API Backend](api/README.md) - Documentación completa del backend
- [Client Frontend](client/README.md) - Documentación completa del frontend
- [Demo Streamlit](demo-version/README-streamlit.md) - Guía de la versión demo
- [Agentes IA](demo-version/README-Agents.md) - Sistema de agentes
- [Base de Datos](demo-db/README-Docker.md) - Configuración de BD

## Licencia

[Especificar licencia del proyecto]

## Contacto

[Información de contacto del equipo]
