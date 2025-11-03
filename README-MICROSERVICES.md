# SERFOR - Arquitectura de Microservicios

Sistema de consulta forestal del Perú con arquitectura de microservicios usando FastAPI (backend) y React + TypeScript + Vite (frontend).

## 🏗️ Arquitectura

```
naturai-serfor-demo/
├── api/                    # Backend FastAPI
│   ├── app/
│   │   ├── core/          # Configuración
│   │   ├── models/        # Modelos Pydantic
│   │   ├── routes/        # Endpoints API
│   │   └── services/      # Lógica de negocio
│   ├── Dockerfile
│   └── requirements.txt
├── client/                 # Frontend React + TypeScript
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── services/      # Clientes API
│   │   └── types/         # TypeScript types
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── agents/                 # Sistema multi-agente (compartido)
├── database/               # Utilidades de BD (compartido)
├── utils/                  # Utilidades (compartido)
└── docker-compose.yml      # Orquestación de servicios
```

## 🚀 Inicio Rápido con Docker

### Pre-requisitos

- Docker Desktop instalado
- Docker Compose v2+
- Variable de entorno `OPENAI_API_KEY`

### 1. Configurar Variables de Entorno

```bash
# En la raíz del proyecto, crear o actualizar .env
echo "OPENAI_API_KEY=tu_api_key_aqui" > .env
```

### 2. Construir y Levantar los Servicios

```bash
# Construir e iniciar todos los servicios
docker-compose up --build

# O en modo detached (background)
docker-compose up --build -d
```

### 3. Acceder a los Servicios

- **Frontend (React)**: http://localhost
- **Backend API (FastAPI)**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **SQL Server**: localhost:1433

### 4. Verificar el Estado

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f api
docker-compose logs -f client
docker-compose logs -f sqlserver

# Ver estado de los contenedores
docker-compose ps
```

### 5. Detener los Servicios

```bash
# Detener servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

## 🔧 Desarrollo Local

### Backend (API)

```bash
cd api

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar servidor de desarrollo
python run.py
```

La API estará disponible en http://localhost:8000

### Frontend (Client)

```bash
cd client

# Instalar dependencias
npm install

# Configurar .env
cp .env.example .env
# Editar .env con la URL de la API

# Ejecutar servidor de desarrollo
npm run dev
```

El frontend estará disponible en http://localhost:5173

## 📡 API Endpoints

### POST /api/query
Procesa una consulta en lenguaje natural sobre datos forestales.

**Request:**
```json
{
  "query": "¿Cuáles son las especies más comunes en Amazonas?",
  "include_workflow": false
}
```

**Response:**
```json
{
  "success": true,
  "final_response": "...",
  "agents_used": ["InterpreterAgent", "ExecutorAgent", "ResponseAgent"],
  "data": [...],
  "sql_queries": [...],
  "visualization_code": [...]
}
```

### GET /api/health
Verifica el estado de la API y la conexión a la base de datos.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-15T10:30:00"
}
```

## 🐳 Servicios Docker

### sqlserver
- **Imagen**: mcr.microsoft.com/mssql/server:2022-latest
- **Puerto**: 1433
- **Usuario**: sa
- **Password**: SerforDB@2025

### api
- **Build**: Dockerfile en api/
- **Puerto**: 8000
- **Depende de**: sqlserver

### client
- **Build**: Dockerfile en client/
- **Puerto**: 80
- **Depende de**: api
- **Servidor**: Nginx

## 🛠️ Comandos Útiles

### Docker

```bash
# Reconstruir solo un servicio
docker-compose up --build api

# Ejecutar comando en un contenedor
docker-compose exec api bash
docker-compose exec sqlserver bash

# Ver logs en tiempo real
docker-compose logs -f api

# Reiniciar un servicio
docker-compose restart api
```

### Base de Datos

```bash
# Conectar a SQL Server desde el contenedor
docker-compose exec sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P SerforDB@2025 -C \
  -Q "SELECT name FROM sys.databases"

# Restaurar base de datos
docker-compose exec sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P SerforDB@2025 -C \
  -i /tmp/DataPilotoIA.sql
```

## 📝 Notas Importantes

1. **CORS**: El backend está configurado para aceptar peticiones desde:
   - http://localhost:5173 (dev)
   - http://localhost:80 (prod)

2. **Proxy**: En desarrollo, Vite usa un proxy para redirigir `/api` al backend.

3. **Volúmenes**:
   - Los logs se guardan en `./logs`
   - Los datos de SQL Server persisten en el volumen `sqlserver_data`

4. **Hot Reload**:
   - Backend: Uvicorn con `--reload`
   - Frontend: Vite HMR activado

## 🔍 Troubleshooting

### Error de conexión a la base de datos
```bash
# Verificar que SQL Server esté corriendo
docker-compose ps sqlserver

# Ver logs de SQL Server
docker-compose logs sqlserver

# Esperar a que el healthcheck pase
docker-compose exec sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P SerforDB@2025 -C -Q "SELECT 1"
```

### Frontend no se conecta al backend
```bash
# Verificar que la API esté corriendo
curl http://localhost:8000/api/health

# Ver logs del contenedor client
docker-compose logs client

# Verificar configuración de CORS en api
docker-compose logs api | grep CORS
```

### Errores de build
```bash
# Limpiar todo y reconstruir
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## 📦 Dependencias Principales

### Backend
- FastAPI: Framework web
- Uvicorn: Servidor ASGI
- Pydantic: Validación de datos
- pyodbc: Conexión a SQL Server
- instantneo: Sistema multi-agente

### Frontend
- React 19: Framework UI
- TypeScript: Tipado estático
- Vite: Build tool
- Axios: Cliente HTTP
- Lucide React: Iconos

## 🚢 Despliegue en Producción

Para producción, considera:

1. Usar variables de entorno seguras
2. Configurar certificados SSL
3. Usar un proxy reverso (Nginx/Traefik)
4. Implementar rate limiting
5. Configurar logs centralizados
6. Usar secretos de Docker/Kubernetes

## 📄 Licencia

Ver archivo LICENSE en la raíz del proyecto.
