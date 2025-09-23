"""
Planner Agent - Creates execution plans based on interpreted requests
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from .task_manager import TaskManager, ExecutionTask
from utils.logger import get_logger
import json

class PlannerAgent(BaseAgent):
    """Agent that creates step-by-step execution plans with task management"""

    def __init__(self):
        self.logger = get_logger()
        super().__init__(
            name="Planner",
            model="gpt-4o",
            role_setup="""Eres un agente planificador especializado en crear planes de ejecución para consultas sobre datos de SERFOR.

Basándote en la interpretación de la consulta del usuario, debes crear un plan paso a paso que incluya:
1. Pasos de validación de datos necesarios
2. Consultas específicas a la base de datos
3. Transformaciones de datos requeridas
4. Cálculos o agregaciones necesarias
5. Formato de presentación final

Cada paso debe ser específico y ejecutable, con:
- description: Descripción clara del paso
- action_type: Tipo de acción (query, validate, transform, calculate, aggregate, format)
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
      "parameters": {"table": "T_GEP_INFRACTORES", "where": "fecha BETWEEN ..."},
      "dependencies": [1],
      "max_retries": 3
    }
  ]
}""",
            temperature=0.3,
            max_token=6000
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create execution plan based on interpreted request

        Args:
            input_data: Dictionary with interpretation results

        Returns:
            Dictionary with task manager and execution plan
        """
        interpretation = input_data.get("interpretation", "")
        user_query = input_data.get("user_query", "")
        schema_info = input_data.get("schema_info", {})

        # Format complete schema for planning
        schema_details = ""
        if schema_info and "tables" in schema_info:
            schema_details = "\n🗄️ ESQUEMA COMPLETO DE BASE DE DATOS:\n"
            for table_name, table_data in schema_info["tables"].items():
                schema_details += f"\n📋 Tabla: {table_data.get('full_name', table_name)}\n"
                schema_details += f"   Descripción: {table_data.get('description', 'Sin descripción')}\n"
                schema_details += f"   Filas estimadas: {table_data.get('estimated_rows', 'Desconocido')}\n"
                schema_details += f"   TODAS LAS COLUMNAS:\n"

                # Include ALL columns with full details
                for col in table_data.get('columns', []):
                    col_desc = col.get('description', 'Sin descripción')
                    nullable = "NULL" if col.get('nullable', True) else "NOT NULL"
                    schema_details += f"     - {col['name']} ({col['type']}, {nullable}): {col_desc}\n"

        prompt = f"""
        Basándote en esta interpretación de la consulta del usuario:

        Consulta original: "{user_query}"

        Interpretación: {interpretation}

        {schema_details}

        🛠️ Skills disponibles para usar:
        - execute_select_query: Ejecutar consultas SQL SELECT simples
        - execute_complex_query: Ejecutar consultas complejas con JOINs entre tablas
        - get_table_schemas: Obtener esquemas de tablas
        - search_table_data: Buscar datos con filtros
        - aggregate_table_data: Agregaciones (COUNT, SUM, AVG, MIN, MAX)
        - count_table_rows: Contar filas de tablas
        - get_table_sample: Obtener muestras de datos

        IMPORTANTE - BASE DE DATOS SQL SERVER:
        - Para consultas que requieren TOP/LIMIT: usar 'TOP N' (ej: SELECT TOP 1 ...)
        - Para paginación: usar 'OFFSET X ROWS FETCH NEXT Y ROWS ONLY'
        - NO usar sintaxis MySQL/PostgreSQL como LIMIT
        - Ejemplos: 'TOP 10', 'TOP 1', 'OFFSET 5 ROWS FETCH NEXT 10 ROWS ONLY'

        🎯 ESTRATEGIAS DE CONSULTA (PRIORIZAR SIMPLICIDAD):

        1. EVALÚA PRIMERO SI PUEDES USAR UNA SOLA TABLA:
           - Para consultas sobre superficie/departamento: T_GEP_TITULOHABILITANTE tiene TX_Departamento,TX_Provincia,TX_Distrito y NU_Superficie
           - Para consultas sobre dispositivos legales: T_GEP_INFRACTORES tiene TX_DispositivoLegal
           - Para consultas sobre multas: T_GEP_INFRACTORES tiene NU_MultaUIT (si es mayor a 0 es que hay multa)
           - Para consultas sobre infractores: T_GEP_INFRACTORES tiene TX_Infractor y TX_TitDeTitHab

        2. SI NECESITAS RELACIONAR AMBAS TABLAS (JOINs VÁLIDOS):
           - Relación: T_GEP_INFRACTORES.TX_TituloHabilitante = T_GEP_TITULOHABILITANTE.TX_CodigoContrato
           - Relación: T_GEP_INFRACTORES.TX_TitDeTitHab = T_GEP_TITULOHABILITANTE.TX_NombreTitular
           - Para JOINs usa execute_complex_query con SQL completo
           - NO separes JOINs en múltiples pasos

        3. REGLAS GENERALES:
        - NO inventes tablas temporales como "resultado_unido"
        - Prefiere menos pasos con consultas más simples
        - NO crear tareas de tipo "format" - el formateo es responsabilidad del Response Agent
        - Los action_types válidos para el Executor son: "validate", "query", "transform", "calculate", "aggregate"

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
        {{"step_id": 1, "action_type": "query", "parameters": {{"query": "SELECT th.TX_NombreTitular FROM Dir.T_GEP_TITULOHABILITANTE th JOIN Dir.T_GEP_INFRACTORES i ON th.TX_NombreTitular = i.TX_Infractor WHERE th.TX_SituacionActual = 'vigente' AND i.NU_MultaUIT > 20"}}}}
        """

        response = self.run(prompt)

        # Log the raw response from the agent
        self.logger.log_agent_activity("planner", "raw_response_received", prompt, response)

        # Clean and parse the response
        cleaned_response = self._clean_json_response(response)

        # Create task manager and populate with tasks
        task_manager = self.create_task_manager_from_plan(cleaned_response)

        return {
            "status": "planned",
            "user_query": user_query,
            "interpretation": interpretation,
            "execution_plan": response,
            "task_manager": task_manager,
            "agent": self.name
        }

    def create_task_manager_from_plan(self, plan_json: str) -> TaskManager:
        """
        Create a TaskManager from the planner's JSON output

        Args:
            plan_json: JSON string with execution plan

        Returns:
            TaskManager with populated tasks
        """
        task_manager = TaskManager()

        try:
            # Log JSON parsing attempt
            self.logger.log_json_parsing("planner", plan_json)

            # Parse JSON plan
            plan_data = json.loads(plan_json)
            steps = plan_data.get("steps", [])

            self.logger.log_json_parsing("planner", plan_json, plan_data)

            # Create task mapping for dependencies
            step_id_to_task_id = {}

            # Create tasks
            for step in steps:
                step_id = step.get("step_id")

                # Convert step dependencies to task IDs
                dependencies = []
                for dep_step_id in step.get("dependencies", []):
                    if dep_step_id in step_id_to_task_id:
                        dependencies.append(step_id_to_task_id[dep_step_id])

                # Create task
                task = ExecutionTask(
                    description=step.get("description", ""),
                    action_type=step.get("action_type", "unknown"),
                    parameters=step.get("parameters", {}),
                    dependencies=dependencies,
                    max_retries=step.get("max_retries", 3)
                )

                # Add task and map step_id to task_id
                task_id = task_manager.add_task(task)
                step_id_to_task_id[step_id] = task_id

        except json.JSONDecodeError as e:
            # Log JSON parsing error
            self.logger.log_json_parsing("planner", plan_json, None, str(e))
            self.logger.log_error("planner_json_parsing", str(e), {"raw_plan": plan_json})

            # Create fallback task if JSON parsing fails
            fallback_task = ExecutionTask(
                description="Plan parsing failed - manual execution required",
                action_type="manual",
                parameters={"raw_plan": plan_json, "error": str(e)},
                dependencies=[],
                max_retries=1
            )
            task_manager.add_task(fallback_task)

        return task_manager

    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response by removing markdown and other unwanted characters"""
        import re

        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)

        # Remove leading/trailing whitespace
        response = response.strip()

        # Fix string concatenation issues (remove + operators in JSON strings)
        # This regex finds and removes + concatenation within JSON strings
        response = re.sub(r'"\s*\+\s*\n\s*"', '', response)
        response = re.sub(r'"\s*\+\s*"', '', response)

        # Find JSON content between first { and last }
        start_idx = response.find('{')
        end_idx = response.rfind('}')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            response = response[start_idx:end_idx + 1]

        self.logger.log_agent_activity("planner", "json_cleaning", response, f"Cleaned to: {response}...")

        return response