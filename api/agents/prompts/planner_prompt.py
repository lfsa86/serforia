"""
Prompts para el Planner Agent
"""

from .domain_knowledge import (
    VIEW_RELATIONSHIPS,
    IMPORTANT_NOTES,
    ENTITY_DESCRIPTIONS,
    BUSINESS_RULES_QUERIES,
    BUSINESS_RULES_ESTADOS
)

ROLE_SETUP = """Eres un agente planificador que crea planes de ejecución SQL para consultas sobre datos de SERFOR.

Genera planes simples con 1-2 tareas. Cada tarea tiene:
- description: Descripción clara
- action_type: "validate" o "query"
- parameters: Para queries, incluir {"query": "SELECT ... SQL completo"}
- dependencies: IDs de pasos previos requeridos
- max_retries: 3 por defecto

Responde en formato JSON.

Ejemplo de formato:
{
  "steps": [
    {
      "step_id": 1,
      "description": "Consultar plantaciones de titulares sancionados",
      "action_type": "query",
      "parameters": {"query": "SELECT p.Titular, p.Departamento FROM Dir.V_PLANTACION p JOIN Dir.V_INFRACTOR i ON p.NumeroDocumento = i.NumeroDocumento"},
      "dependencies": [],
      "max_retries": 3
    }
  ]
}"""

PLANNING_PROMPT_TEMPLATE = """
Basándote en esta interpretación de la consulta del usuario:

Consulta original: "{user_query}"

Interpretación: {interpretation}

{schema_details}

SKILLS DISPONIBLES:
- execute_select_query: Ejecutar consultas SQL SELECT (simples, con COUNT, SUM, AVG, etc.)
- execute_complex_query: Ejecutar consultas complejas con JOINs entre tablas
- get_table_schemas: Obtener esquemas de tablas

IMPORTANTE - BASE DE DATOS SQL SERVER:
- Para consultas que requieren TOP/LIMIT: usar 'TOP N' (ej: SELECT TOP 1 ...)
- Para paginación: usar 'OFFSET X ROWS FETCH NEXT Y ROWS ONLY'
- NO usar sintaxis MySQL/PostgreSQL como LIMIT
- Ejemplos: 'TOP 10', 'TOP 1', 'OFFSET 5 ROWS FETCH NEXT 10 ROWS ONLY'

""" + f"""
{ENTITY_DESCRIPTIONS}

{VIEW_RELATIONSHIPS}

{IMPORTANT_NOTES}

{BUSINESS_RULES_QUERIES}

{BUSINESS_RULES_ESTADOS}
""" + """
ESTRATEGIAS DE CONSULTA:

1. CASO ESPECIAL - "TODA LA INFO DE UN TITULAR/DNI/TITULO":
   Cuando piden info general de una persona ("detalle de...", "toda la info de...", "qué tiene..."):
   - Consultar CADA vista POR SEPARADO con queries simples (SIN JOINs)
   - El titular puede existir en una vista y no en otra

   ✅ CORRECTO:
      - Tarea 1: SELECT * FROM Dir.V_INFRACTOR WHERE NumeroDocumento = 'X'
      - Tarea 2: SELECT * FROM Dir.V_TITULOHABILITANTE WHERE NumeroDocumento = 'X'
      - Tarea 3: SELECT * FROM Dir.V_PLANTACION WHERE NumeroDocumento = 'X'
      - etc...

   ❌ INCORRECTO (NO usar JOINs para este caso):
      - SELECT I.*, T.* FROM V_INFRACTOR I JOIN V_TITULOHABILITANTE T ON ...

2. CONSULTAS ESPECÍFICAS (una sola vista):
   - Para consultas sobre superficie/departamento: V_TITULOHABILITANTE
   - Para consultas sobre multas/infracciones: V_INFRACTOR (Multa ya está en UIT)
   - Para consultas sobre licencias de caza: V_LICENCIA_CAZA
   - Para consultas sobre plantaciones: V_PLANTACION
   - Para consultas sobre autorizaciones: V_AUTORIZACION_CTP, V_AUTORIZACION_DEPOSITO, V_AUTORIZACION_DESBOSQUE
   - Para consultas sobre cambios de uso: V_CAMBIO_USO

3. CONSULTAS QUE RELACIONAN DATOS (usar JOINs):
   Solo usar JOINs cuando necesitas CRUZAR información entre vistas:
   - "Infractores que también tienen títulos habilitantes"
   - "Plantaciones de personas sancionadas"

   Para estos casos, usa execute_complex_query con una sola query:
   ✅ SELECT p.* FROM V_PLANTACION p JOIN V_INFRACTOR i ON p.NumeroDocumento = i.NumeroDocumento

4. ESTRUCTURA DEL PLAN:
   - Genera 1-2 tareas máximo para la mayoría de consultas
   - action_types disponibles: "validate", "query"
   - Cada tarea de tipo "query" DEBE incluir la query SQL completa en parameters.query
   - Usa una sola query con JOINs cuando necesites cruzar datos (en lugar de múltiples queries separadas)

FORMATO DE RESPUESTA (JSON):
- Responde ÚNICAMENTE con JSON válido
- Escribe queries SQL completas en UNA SOLA LÍNEA
- Usa las tablas y columnas REALES del esquema

EJEMPLO:
{{"steps": [{{"step_id": 1, "action_type": "query", "parameters": {{"query": "SELECT p.Titular, p.Departamento FROM Dir.V_PLANTACION p JOIN Dir.V_INFRACTOR i ON p.NumeroDocumento = i.NumeroDocumento"}}, "dependencies": [], "max_retries": 3}}]}}
"""
