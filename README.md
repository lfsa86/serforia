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
- **uv** - Gestor de paquetes Python (recomendado para desarrollo)
- **ODBC Driver 18 for SQL Server** - Para conexión a BD
- **OpenAI API Key** - Para los agentes de IA

## Inicio Rápido

### 1. Configurar y Ejecutar API

Ver [api/README.md](api/README.md) para más detalles.

### 2. Configurar y Ejecutar Client

Ver [client/README.md](client/README.md) para más detalles.

### 3. Acceder a las Aplicaciones

- **Frontend:** http://your-url:5173
- **API Docs:** http://your-url:8000/docs
- **API Health:** http://your-url:8000/health

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

## Deployment

Cada servicio es independiente y puede ser desplegado por separado
