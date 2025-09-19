"""
Orchestrator - Coordinates the multi-agent system workflow
"""
from typing import Dict, Any
from .interpreter_agent import InterpreterAgent
from .planner_agent import PlannerAgent
from .executor_agent import ExecutorAgent
from .response_agent import ResponseAgent
from database.schema_mapper import DynamicSchemaMapper
from utils.logger import get_logger

class AgentOrchestrator:
    """Orchestrates the workflow between all agents in the SERFOR system"""

    def __init__(self):
        """Initialize all agents and load schema information"""
        # Initialize logger
        self.logger = get_logger()

        # Load schema information
        self.schema_mapper = DynamicSchemaMapper()
        self.schema_info = self.schema_mapper.get_schema_for_ai()

        self.logger.log_agent_activity(
            "orchestrator",
            "schema_loading",
            None,
            f"Schema loaded: {len(self.schema_info.get('tables', {}))} tables"
        )

        print(f"📋 Esquema cargado: {len(self.schema_info.get('tables', {}))} tablas disponibles")

        self.interpreter = InterpreterAgent()
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.response_agent = ResponseAgent()

        self.agents = {
            "interpreter": self.interpreter,
            "planner": self.planner,
            "executor": self.executor,
            "response": self.response_agent
        }

    def process_user_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query through the complete agent pipeline with task management

        Args:
            user_query: The user's natural language query

        Returns:
            Dictionary with the complete processing results
        """
        # Log user query
        self.logger.log_user_query(user_query)

        workflow_data = {
            "user_query": user_query,
            "schema_info": self.schema_info  # Include schema in all steps
        }

        try:
            # Step 1: Interpret the user query
            print("🔍 Interpretando consulta...")
            self.logger.log_agent_activity("orchestrator", "starting_interpretation", workflow_data)
            interpretation_result = self.interpreter.process(workflow_data)
            self.logger.log_agent_activity("interpreter", "process_completed", workflow_data, interpretation_result)
            workflow_data.update(interpretation_result)

            # Step 2: Create execution plan with task management
            print("📋 Creando plan de ejecución...")
            self.logger.log_agent_activity("orchestrator", "starting_planning", workflow_data)
            planning_result = self.planner.process(workflow_data)
            self.logger.log_agent_activity("planner", "process_completed", workflow_data, planning_result)
            workflow_data.update(planning_result)

            # Show planned tasks
            task_manager = planning_result.get("task_manager")
            if task_manager:
                print(f"📊 Plan creado con {len(task_manager.tasks)} tareas")
                for task in task_manager.tasks:
                    print(f"   - {task.description} [{task.action_type}]")
                    self.logger.log_task_execution(task.id, task.description, "planned")

            # Step 3: Execute the plan with task management
            print("⚡ Ejecutando plan con gestión de tareas...")
            self.logger.log_agent_activity("orchestrator", "starting_execution", workflow_data)
            execution_result = self.executor.process(workflow_data)
            self.logger.log_agent_activity("executor", "process_completed", workflow_data, execution_result)
            workflow_data.update(execution_result)

            # Show execution summary
            exec_summary = execution_result.get("execution_summary", {})
            if exec_summary:
                print(f"📈 Ejecución completada:")
                for status, count in exec_summary.get("status_counts", {}).items():
                    if count > 0:
                        print(f"   - {status}: {count} tareas")

            # Step 4: Format response
            print("📝 Formateando respuesta...")
            self.logger.log_agent_activity("orchestrator", "starting_response_generation", workflow_data)
            response_result = self.response_agent.process(workflow_data)
            self.logger.log_agent_activity("response", "process_completed", workflow_data, response_result)
            workflow_data.update(response_result)

            return {
                "success": True,
                "workflow_data": workflow_data,
                "final_response": response_result.get("final_response", ""),
                "execution_summary": exec_summary,
                "agents_used": [agent.name for agent in self.agents.values()],
                "task_details": execution_result.get("task_manager_state", {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_data": workflow_data
            }

    def get_agent_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about all agents"""
        return {name: agent.get_info() for name, agent in self.agents.items()}

    def test_agents(self) -> Dict[str, bool]:
        """Test if all agents are working properly"""
        test_results = {}

        for name, agent in self.agents.items():
            try:
                # Simple test prompt
                test_response = agent.run("Test de conectividad")
                test_results[name] = bool(test_response)
            except Exception as e:
                test_results[name] = False
                print(f"❌ Error testing {name}: {e}")

        return test_results