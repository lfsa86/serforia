"""
Executor Agent - Executes database queries and data operations
"""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from .task_manager import TaskManager, ExecutionTask, TaskStatus
from instantneo import SkillManager
import time
from typing import List
from utils.logger import get_logger

class ExecutorAgent(BaseAgent):
    """Agent that executes database operations using specialized skills with task management"""

    def __init__(self):
        # Initialize logger
        self.logger = get_logger()

        # Initialize skill manager for database operations
        skills = SkillManager()

        # Register database skills
        from database.skills import (
            execute_select_query,
            execute_complex_query,
            get_table_schemas,
            get_table_sample,
            count_table_rows,
            search_table_data,
            aggregate_table_data,
            test_database_connection,
            refresh_database_schema
        )

        skills.register_skill(execute_select_query)
        skills.register_skill(execute_complex_query)
        skills.register_skill(get_table_schemas)
        skills.register_skill(get_table_sample)
        skills.register_skill(count_table_rows)
        skills.register_skill(search_table_data)
        skills.register_skill(aggregate_table_data)
        skills.register_skill(test_database_connection)
        skills.register_skill(refresh_database_schema)

        super().__init__(
            name="Executor",
            role_setup="""Eres un agente ejecutor especializado en realizar consultas y operaciones sobre la base de datos SERFOR_BDDWH.

Tienes acceso a skills especializadas para:
- execute_select_query: Consultas SELECT simples
- execute_complex_query: Consultas complejas con JOINs entre tablas
- get_table_schemas: Obtener esquemas de tablas
- search_table_data: Buscar datos con filtros
- aggregate_table_data: Agregaciones (COUNT, SUM, AVG, MIN, MAX)
- count_table_rows: Contar filas de tablas
- get_table_sample: Obtener muestras de datos

VISTAS DISPONIBLES:
- Dir.V_INFRACTOR: Información de infracciones forestales
- Dir.V_TITULOHABILITANTE: Información de títulos habilitantes
- Dir.V_LICENCIA_CAZA: Licencias de caza
- Dir.V_PLANTACION: Plantaciones forestales
- Dir.V_AUTORIZACION_CTP: Autorizaciones CTP
- Dir.V_AUTORIZACION_DEPOSITO: Autorizaciones de depósito
- Dir.V_AUTORIZACION_DESBOSQUE: Autorizaciones de desbosque
- Dir.V_CAMBIO_USO: Cambios de uso

IMPORTANTE - SINTAXIS SQL SERVER:
- USA 'TOP N' en lugar de 'LIMIT N'
- Para paginación: 'OFFSET X ROWS FETCH NEXT Y ROWS ONLY'
- NO combines TOP con OFFSET en la misma query
- Ejemplos correctos:
  * SELECT TOP 10 * FROM tabla ORDER BY columna
  * SELECT * FROM tabla ORDER BY columna OFFSET 5 ROWS FETCH NEXT 10 ROWS ONLY

ESTRATEGIA PARA CONSULTAS COMPLEJAS:
- Para consultas que requieren relacionar ambas tablas, usa execute_complex_query
- Construye queries SQL completas con JOINs en lugar de múltiples pasos
- NO inventes tablas temporales ni resultados intermedios
- Usa las columnas reales que existen en el esquema

Ejecutas tareas individuales según su tipo de acción:
- validate: Validar parámetros y datos
- query: Realizar consultas SQL (simple o compleja según necesidad)
- transform: Procesar datos ya obtenidos
- calculate: Realizar cálculos sobre datos existentes
- aggregate: Agregar datos con funciones SQL
- format: Formatear resultados finales

Para cada tarea, proporciona un resultado claro y estructurado.
Si encuentras errores, describe específicamente qué falló y por qué.""",
            temperature=0.1,
            skills=skills
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tasks using the task manager

        Args:
            input_data: Dictionary with task manager

        Returns:
            Dictionary with execution results
        """
        task_manager: TaskManager = input_data.get("task_manager")
        user_query = input_data.get("user_query", "")

        if not task_manager:
            return {
                "status": "error",
                "error": "No task manager provided",
                "agent": self.name
            }

        # Execute tasks loop
        execution_results = []
        max_iterations = 50  # Prevent infinite loops

        for iteration in range(max_iterations):
            # Get next executable task
            current_task = task_manager.get_next_executable_task()

            if not current_task:
                # No more tasks to execute
                break

            print(f"🔄 Ejecutando tarea {iteration + 1}: {current_task.description}")

            # Execute the task
            result = self.execute_single_task(current_task)
            execution_results.append(result)

            # Check if execution is complete
            if task_manager.is_execution_complete():
                break

            # Small delay to prevent overwhelming the system
            time.sleep(0.1)

        # Get final summary
        execution_summary = task_manager.get_execution_summary()

        # Note: Recovery is now handled automatically via retry context in generate_task_prompt

        return {
            "status": "executed",
            "user_query": user_query,
            "execution_results": execution_results,
            "execution_summary": task_manager.get_execution_summary(),
            "task_manager_state": task_manager.to_dict(),
            "agent": self.name
        }

    def execute_single_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """
        Execute a single task

        Args:
            task: The task to execute

        Returns:
            Dictionary with task execution result
        """
        task.start_execution()

        try:
            # Generate execution prompt based on task type
            prompt = self.generate_task_prompt(task)

            # Execute using the agent
            response = self.run(prompt)

            # Check if the response indicates an error
            if self._is_error_response(response):
                error_message = f"Task execution failed: {response}"
                task.complete_failure(error_message)
                print(f"❌ Tarea fallida: {task.description} - {error_message}")
                
                return {
                    "task_id": task.id,
                    "status": "failed",
                    "description": task.description,
                    "error": error_message,
                    "response": response,
                    "retry_count": task.retry_count
                }

            # Mark task as completed successfully
            task.complete_success(response)
            print(f"✅ Tarea completada: {task.description}")

            return {
                "task_id": task.id,
                "status": "success",
                "description": task.description,
                "result": response,
                "execution_time": (task.completed_at - task.started_at).total_seconds() if task.completed_at and task.started_at else 0
            }

        except Exception as e:
            error_message = f"Error executing task: {str(e)}"
            task.complete_failure(error_message)
            print(f"❌ Excepción en tarea: {task.description} - {error_message}")

            return {
                "task_id": task.id,
                "status": "failed",
                "description": task.description,
                "error": error_message,
                "retry_count": task.retry_count
            }

    def _is_error_response(self, response: str) -> bool:
        """Check if the response indicates an error"""
        error_indicators = [
            "error",
            "Error",
            "ERROR",
            "failed",
            "Failed",
            "FAILED",
            "exception",
            "Exception",
            "not JSON serializable",
            "query validation failed",
            "connection failed",
            "no se puede",
            "no se pudo",
            "falló",
            "fallo"
        ]

        return any(indicator in response for indicator in error_indicators)

    def generate_task_prompt(self, task: ExecutionTask) -> str:
        """Generate appropriate prompt for task execution with retry context"""
        base_prompt = f"""
        Ejecuta la siguiente tarea:

        Descripción: {task.description}
        Tipo de acción: {task.action_type}
        Parámetros: {task.parameters}
        """

        # Add retry context if this is not the first attempt
        if task.retry_count > 0:
            base_prompt += f"""

        IMPORTANTE - INTENTO #{task.retry_count + 1}:
        Tu intento anterior falló con el siguiente error:
        {task.error_message}

        Cambia tu estrategia para evitar el mismo error. Considera:
        - Usar una skill diferente
        - Simplificar la consulta
        - Probar un enfoque alternativo
        """

        # Customize prompt based on action type
        if task.action_type == "validate":
            return base_prompt + "\nValida los parámetros y datos especificados. Retorna 'VALID' si todo está correcto, o describe los problemas encontrados."

        elif task.action_type == "query":
            return base_prompt + "\nEjecuta la consulta especificada. Si necesitas relacionar tablas, usa execute_complex_query con un JOIN completo. NO uses tablas temporales. Retorna los resultados estructurados."

        elif task.action_type == "transform":
            return base_prompt + "\nTransforma los datos según los parámetros. Retorna los datos transformados."

        elif task.action_type == "calculate":
            return base_prompt + "\nRealiza los cálculos especificados. Retorna los resultados numéricos."

        elif task.action_type == "aggregate":
            return base_prompt + "\nAgrega los datos según los parámetros. Retorna el resumen agregado."

        elif task.action_type == "format":
            # Format tasks should not be handled by executor - skip and mark as failed
            return "ERROR: Las tareas de tipo 'format' deben ser manejadas por el Response Agent, no el Executor."

        else:
            return base_prompt + "\nEjecuta la operación especificada y retorna el resultado."

    def attempt_recovery(self, task_manager: TaskManager) -> List[Dict[str, Any]]:
        """
        Attempt to recover from failed tasks

        Args:
            task_manager: The task manager with failed tasks

        Returns:
            List of recovery execution results
        """
        recovery_results = []

        # Create recovery tasks
        recovery_tasks = task_manager.create_recovery_plan()

        for recovery_task in recovery_tasks:
            print(f"🔧 Ejecutando recuperación: {recovery_task.description}")

            # Add recovery task to manager
            task_manager.add_task(recovery_task)

            # Execute recovery task
            result = self.execute_single_task(recovery_task)
            recovery_results.append(result)

        return recovery_results