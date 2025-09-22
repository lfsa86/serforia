# 🌲 SERFOR Streamlit App

Interfaz web interactiva para el sistema multi-agente de consultas forestales de SERFOR.

## 🚀 Características

- **Interfaz Visual Intuitiva**: Diseño moderno con tema forestal
- **Visualización en Tiempo Real**: Seguimiento del progreso de consultas paso a paso
- **Tablas Interactivas**: Resultados mostrados en formato de tabla con filtros y descarga
- **Historial de Consultas**: Registro de todas las consultas realizadas
- **Estado del Sistema**: Monitoreo en tiempo real de agentes y base de datos
- **Logging Avanzado**: Visualización de consultas SQL ejecutadas

## 📋 Requisitos Previos

1. **Base de datos configurada**: Asegúrate de que el contenedor Docker esté corriendo
2. **Dependencias instaladas**: Ejecuta `pip install -r requirements.txt`
3. **Variables de entorno**: Archivo `.env` configurado

## 🎯 Uso Rápido

### Opción 1: Script de lanzamiento
```bash
python run_streamlit.py
```

### Opción 2: Comando directo
```bash
streamlit run streamlit_app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 🎨 Interfaz de Usuario

### Panel Principal
- **Área de consulta**: Campo de texto para escribir consultas en lenguaje natural
- **Botón de procesamiento**: Inicia el análisis de la consulta
- **Visualización de progreso**: Muestra las 4 etapas del proceso:
  - 🔍 Interpretación
  - 📋 Planificación
  - ⚡ Ejecución
  - 📝 Respuesta

### Sidebar - Estado del Sistema
- **Estado de Agentes**: ✅/❌ para cada agente (Interpreter, Planner, Executor, Response)
- **Información de BD**: Número de tablas disponibles
- **Datos de Sesión**: ID de sesión y contador de consultas

### Resultados
- **Métricas**: Total de registros y columnas encontradas
- **Tabla Interactiva**: Datos en formato DataFrame con funcionalidades:
  - Ordenamiento por columnas
  - Filtrado
  - Paginación automática
- **Descarga**: Botón para exportar resultados en CSV
- **Resumen**: Análisis detallado en texto formateado

### Sección de Monitoreo
- **Progreso de Tareas**: Barra de progreso con métricas (completadas/fallidas/pendientes)
- **Consultas SQL**: Visualización de las queries ejecutadas con sintaxis highlighting
- **Historial**: Últimas 5 consultas con estados y timestamps

## 🔧 Funcionalidades Avanzadas

### Visualización en Tiempo Real
- Actualización de progreso mientras se procesa la consulta
- Estados visuales para cada etapa del proceso
- Indicadores de éxito/error en tiempo real

### Formato Inteligente de Resultados
- Detección automática de tablas en respuestas
- Conversión de JSON a DataFrames
- Formateo limpio de texto sin markdown

### Gestión de Sesiones
- Cada sesión tiene un ID único
- Logging completo de todas las actividades
- Persistencia del historial durante la sesión

## 📊 Ejemplo de Consulta

```
Necesito identificar a los titulares que tienen títulos habilitantes vigentes y que, además, cuentan con infracciones sancionadas con multas mayores a 20 UIT.
```

**Resultado esperado:**
- Tabla con columnas: Titular, Infractor, Multa (UIT)
- Métricas de registros encontrados
- Análisis detallado del resultado

## 🛠️ Solución de Problemas

### Error de conexión a BD
- Verifica que Docker esté corriendo: `docker ps`
- Confirma las variables de entorno en `.env`

### Error de dependencias
```bash
pip install --upgrade -r requirements.txt
```

### Puerto ocupado
Si el puerto 8501 está en uso, cambia el puerto:
```bash
streamlit run streamlit_app.py --server.port 8502
```

## 📝 Logs y Debugging

Los logs se guardan automáticamente en:
- `logs/session_YYYYMMDD_HHMMSS.json` - Datos estructurados
- `logs/detailed_YYYYMMDD_HHMMSS.txt` - Log detallado legible

## 🎯 Próximas Mejoras

- [ ] Gráficos y visualizaciones de datos
- [ ] Exportación a múltiples formatos (Excel, PDF)
- [ ] Filtros avanzados en tablas
- [ ] Modo oscuro/claro
- [ ] Guardado de consultas favoritas