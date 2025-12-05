"""
Prompts para el Planner Agent
"""

from .domain_knowledge import VIEW_RELATIONSHIPS, IMPORTANT_NOTES, ENTITY_DESCRIPTIONS

ROLE_SETUP = """Eres un agente planificador especializado en crear planes de ejecución para consultas sobre datos de SERFOR.

Basándote en la interpretación de la consulta del usuario, debes crear un plan paso a paso que incluya:
1. Pasos de validación de datos necesarios
2. Consultas específicas a la base de datos
3. Transformaciones de datos requeridas
4. Cálculos o agregaciones necesarias
5. Formato de presentación final

Cada paso debe ser específico y ejecutable, con:
- description: Descripción clara del paso
- action_type: Tipo de acción (query, validate, transform, calculate, aggregate)
- parameters: Parámetros específicos necesarios
- dependencies: IDs de pasos que deben completarse antes (usar números: 1, 2, 3...)
- max_retries: Número máximo de reintentos (por defecto 3)

Responde SIEMPRE en formato JSON con una lista de pasos ordenados.

Ejemplo de formato:
{
  "steps": [
    {
      "step_id": 1,
      "description": "Validar parámetros de fecha",
      "action_type": "validate",
      "parameters": {"date_range": "2022-01-01 to 2022-12-31"},
      "dependencies": [],
      "max_retries": 2
    },
    {
      "step_id": 2,
      "description": "Consultar infractores por fecha",
      "action_type": "query",
      "parameters": {"table": "V_INFRACTOR", "where": "FechaResolucion BETWEEN ..."},
      "dependencies": [1],
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

4. REGLAS GENERALES:
   - NO inventes tablas temporales como "resultado_unido"
   - MINIMIZA el número de tareas: una consulta compleja es mejor que varias simples
   - Si puedes resolver con 1 tarea, NO uses 2
   - NO crear tareas de tipo "format" - el formateo es responsabilidad del Response Agent
   - Los action_types válidos son: "validate", "query", "transform", "calculate", "aggregate"

Crea un plan de ejecución detallado en formato JSON con los pasos necesarios para responder la consulta.

IMPORTANTE:
- Usa las tablas y columnas REALES del esquema mostrado arriba
- Cada paso debe especificar exactamente qué columnas y tablas usar
- Usa el formato JSON especificado con step_id, description, action_type, parameters, dependencies y max_retries
- RESPONDE ÚNICAMENTE CON JSON VÁLIDO, SIN TEXTO ADICIONAL ANTES O DESPUÉS
- NO uses concatenación de strings con + dentro del JSON
- Escribe consultas SQL completas en UNA SOLA LÍNEA
- Para action_type usa solo: "validate", "query", "transform", "calculate", "aggregate" (NO "format")

EJEMPLO VÁLIDO:
{{"step_id": 1, "action_type": "query", "parameters": {{"query": "SELECT th.Titular FROM Dir.V_TITULOHABILITANTE th JOIN Dir.V_INFRACTOR i ON th.TituloHabilitante = i.TituloHabilitante WHERE th.Situacion = 'vigente' AND i.Multa > 20"}}}}
"""
