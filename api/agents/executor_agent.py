"""
Executor Agent - Executes database queries and data operations
"""
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from .task_manager import TaskManager, ExecutionTask, TaskStatus
from .prompts.executor_prompt import ROLE_SETUP, TASK_PROMPT_BASE, TASK_PROMPTS
from .utils import format_schema_for_prompt
from instantneo import SkillManager
import time
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
            test_database_connection,
            refresh_database_schema
        )

        skills.register_skill(execute_select_query)
        skills.register_skill(execute_complex_query)
        skills.register_skill(get_table_schemas)
        skills.register_skill(test_database_connection)
        skills.register_skill(refresh_database_schema)

        super().__init__(
            name="Executor",
            role_setup=ROLE_SETUP,
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
        schema_info = input_data.get("schema_info", {})

        # Store formatted schema for use in task prompts
        self.schema_details = format_schema_for_prompt(schema_info)

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
        """Generate appropriate prompt for task execution with schema context"""
        # Include schema in prompt
        schema_context = getattr(self, 'schema_details', '')

        base_prompt = TASK_PROMPT_BASE.format(
            description=task.description,
            action_type=task.action_type,
            parameters=task.parameters,
            schema_details=schema_context
        )

        # Add retry context if this is not the first attempt
        if task.retry_count > 0:
            base_prompt += f"""
⚠️ INTENTO #{task.retry_count + 1} - ERROR ANTERIOR:
{task.error_message}

Usa SOLO las columnas que existen en el schema de arriba.
"""

        # Get action-specific prompt or default
        action_suffix = TASK_PROMPTS.get(task.action_type, TASK_PROMPTS["default"])

        return base_prompt + "\n" + action_suffix

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