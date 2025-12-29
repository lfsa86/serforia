# SERFOR Client - React Frontend

Aplicación web React + Vite para interactuar con la API de consultas en lenguaje natural de SERFOR.

## Requisitos Previos

- Node.js 18.x o superior
- npm (incluido con Node.js)
- API backend corriendo en http://localhost:8000

### Instalar Node.js

**Windows:**
Descarga el instalador desde: https://nodejs.org/

**macOS:**
```bash
brew install node
```

**Linux (Ubuntu/Debian):**
```bash
# Añadir repositorio
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -

# Instalar Node.js
sudo yum install -y nodejs

# Verificar instalación (debe mostrar v20.x.x)
node -v
npm -v
```

## Instalación

1. Navega a la carpeta del cliente:
```bash
cd client
```

2. Instala las dependencias:
```bash
npm install
```

## Configuración

1. Crea un archivo `.env` en la carpeta `client/`:

- Para producción con sub-ruta específica
VITE_APP_URL=/estadistico/serforia/api
VITE_BASE_PATH=/estadistico/serforia/
- Para desarrollo
VITE_API_URL=http://your-url:8000/api
VITE_BASE_PATH=/

```env
VITE_APP_URL=/estadistico/serforia/api
VITE_BASE_PATH=/estadistico/serforia/
```

## Ejecución

### Modo Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en: http://localhost:5173

### Build para Producción

```bash
npm run build
```

Los archivos optimizados se generarán en la carpeta `dist/`.

Consultar la documentación de despliegue.

## Estructura del Proyecto

```
client/
├── src/
│   ├── components/    # Componentes React
│   ├── services/      # Servicios API
│   ├── App.tsx        # Componente principal
│   └── main.tsx       # Punto de entrada
├── public/            # Archivos estáticos
├── index.html         # HTML base
├── package.json       # Dependencias y scripts
├── vite.config.ts     # Configuración de Vite
├── tsconfig.json      # Configuración de TypeScript
└── README.md          # Esta documentación
```

## Scripts Disponibles

```bash
# Iniciar servidor de desarrollo
npm run dev

# Compilar para producción
npm run build

# Preview del build de producción
npm run preview

# Linting del código
npm run lint
```

## Tecnologías Utilizadas

- **React 20** - Framework de UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **Axios** - Cliente HTTP
- **React Markdown** - Renderizado de markdown
- **Lucide React** - Íconos

## Configuración de CORS

Asegúrate de que la API backend tenga configurado CORS para permitir conexiones desde el cliente. En el archivo `.env` de la API, debe incluir:

```env
CORS_ORIGINS=http://your-url:5173,http://your-url:3000
```

## Troubleshooting

### Error de conexión a la API
- Verifica que la API esté corriendo en http://your-url:8000
- Revisa la configuración de `VITE_API_URL` en el archivo `.env`
- Confirma la configuración de CORS en el backend

### Puerto 5173 en uso
```bash
# El dev server de Vite automáticamente usará el siguiente puerto disponible
# O puedes especificar un puerto diferente:
npm run dev -- --port 3000
```

### Errores de TypeScript
```bash
# Verifica los tipos
npx tsc --noEmit

# Reinstala las dependencias
rm -rf node_modules package-lock.json
npm install
```

### Problemas con dependencias
```bash
# Limpia caché de npm
npm cache clean --force

# Reinstala todo
rm -rf node_modules package-lock.json
npm install
```

## Desarrollo

### Agregar nueva dependencia

```bash
npm install nombre-paquete
```

### Agregar dependencia de desarrollo

```bash
npm install -D nombre-paquete
```

## Build y Deployment

Para producción, después de ejecutar `npm run build`, puedes servir los archivos estáticos de la carpeta `dist/` con cualquier servidor web.

