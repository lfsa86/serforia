"""
Planner Agent - Creates execution plans based on interpreted requests
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from .task_manager import TaskManager, ExecutionTask
import json

class PlannerAgent(BaseAgent):
    """Agent that creates step-by-step execution plans with task management"""

    def __init__(self):
        super().__init__(
            name="Planner",
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
            temperature=0.3
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

        prompt = f"""
        Basándote en esta interpretación de la consulta del usuario:

        Consulta original: "{user_query}"

        Interpretación: {interpretation}

        Crea un plan de ejecución detallado en formato JSON con los pasos necesarios para responder la consulta.

        El plan debe considerar:
        - Acceso a las tablas: Dir.T_GEP_INFRACTORES y Dir.T_GEP_TITULOHABILITANTE
        - Validaciones necesarias
        - Consultas SQL específicas
        - Procesamiento de resultados
        - Formato de presentación

        IMPORTANTE: Usa el formato JSON especificado con step_id, description, action_type, parameters, dependencies y max_retries.
        """

        response = self.run(prompt)

        # Create task manager and populate with tasks
        task_manager = self.create_task_manager_from_plan(response)

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
            # Parse JSON plan
            plan_data = json.loads(plan_json)
            steps = plan_data.get("steps", [])

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