"""
Planner Agent - Creates execution plans based on interpreted requests
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from .task_manager import TaskManager, ExecutionTask
from .prompts.planner_prompt import ROLE_SETUP, PLANNING_PROMPT_TEMPLATE
from .utils import format_schema_for_prompt
from utils.logger import get_logger
import json

class PlannerAgent(BaseAgent):
    """Agent that creates step-by-step execution plans with task management"""

    def __init__(self):
        self.logger = get_logger()
        super().__init__(
            name="Planner",
            model="gpt-4o",
            role_setup=ROLE_SETUP,
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

        # Format schema using shared utility
        schema_details = format_schema_for_prompt(schema_info)

        prompt = PLANNING_PROMPT_TEMPLATE.format(
            user_query=user_query,
            interpretation=interpretation,
            schema_details=schema_details
        )

        response = self.run(prompt)

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
            # Log JSON parsing error
            self.logger.log_json_parsing("planner", plan_json, None, str(e))

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

        return response