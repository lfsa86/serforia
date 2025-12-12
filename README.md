# SERFOR - Sistema de Consultas con Lenguaje Natural

Sistema de consultas en lenguaje natural para datos de SERFOR, utilizando agentes de IA para procesar y visualizar información forestal.

## Arquitectura del Proyecto

```
naturai-serfor-demo/
├── api/                  # Backend FastAPI
└── client/               # Frontend React
```

### Componentes

1. **API Backend** (`/api`) - FastAPI + Python
   - Procesamiento de consultas en lenguaje natural
   - Agentes de IA con OpenAI
   - Sistema autocontenido con sus propios `agents/`, `database/`, `utils/`
   - Gestión con **uv** para desarrollo local y **pip** para repos remotos
   - Ver documentación completa: [api/README.md](api/README.md)

2. **Client Frontend** (`/client`) - React + TypeScript + Vite
   - Interfaz web interactiva moderna
   - Comunicación con API via REST
   - Visualización de resultados y gráficos
   - Ver documentación completa: [client/README.md](client/README.md)

## Requisitos del Sistema

- **Python 3.11+** - Para la API
- **Node.js 18+** - Para el frontend
- **uv** - Gestor de paquetes Python (opcional, recomendado para desarrollo)
- **ODBC Driver 18 for SQL Server** - Para conexión a BD
- **OpenAI API Key** - Para los agentes de IA

## Inicio Rápido

### 1. Configurar y Ejecutar API

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

### 2. Configurar y Ejecutar Client

```bash
cd client

npm install
npm run dev
```

Ver [client/README.md](client/README.md) para más detalles.

### 3. Acceder a las Aplicaciones

- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

## Estructura del Proyecto

```
naturai-serfor-demo/
│
├── api/                          # Backend API
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
├── client/                       # Frontend React
│   ├── src/
│   │   ├── components/           # Componentes UI
│   │   ├── services/             # Cliente API
│   │   ├── types/                # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   └── README.md
│
├── .gitignore
└── README.md
```

## Configuración de Variables de Entorno

### API (`api/.env`)

```env
# Database
DB_SERVER=localhost
DB_PORT=1433
DB_DATABASE=DATABASE
DB_USERNAME=sa
DB_PASSWORD=DB@2025
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

## Comandos Útiles

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

## Troubleshooting

### API

**Error de conexión a BD:**
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

## Deployment

Cada servicio es independiente y puede ser desplegado por separado:

- **API**: Ver [api/README.md](api/README.md)
- **Client**: Ver [client/README.md](client/README.md)

## Documentación Adicional

- [API Backend](api/README.md) - Documentación completa del backend
- [Client Frontend](client/README.md) - Documentación completa del frontend
