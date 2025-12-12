"""
Orchestrator - Coordinates the multi-agent system workflow
"""
import json
from typing import Dict, Any
from .interpreter_agent import InterpreterAgent
from .planner_agent import PlannerAgent
from .executor_agent import ExecutorAgent
from .response_agent import ResponseAgent
from .visualization_agent import VisualizationAgent
from database.schema_mapper import DynamicSchemaMapper
from utils.logger import get_logger
from utils.debug_serializer import debug_workflow_data

class AgentOrchestrator:
    """Orchestrates the workflow between all agents in the SERFOR system"""

    def __init__(self):
        """Initialize all agents and load schema information"""
        # Initialize logger
        self.logger = get_logger()

        # Load schema information
        self.schema_mapper = DynamicSchemaMapper()

        # Try to load from cache first, if not available, discover from DB
        self.schema_info = self.schema_mapper.get_schema_for_ai()

        # If no schema loaded, try to discover from database
        if not self.schema_info.get('tables') or len(self.schema_info.get('tables', {})) == 0:
            self.logger.log_agent_activity(
                "orchestrator",
                "schema_discovery",
                None,
                "No cached schema found, attempting to discover from database"
            )
            print("🔍 No hay cache de esquema, descubriendo desde la base de datos...")

            try:
                import os
                from database.connection_manager import DatabaseConnectionManager

                # Get database connection
                db_manager = DatabaseConnectionManager()
                conn_string = db_manager.get_connection_string()

                # Discover schema
                self.schema_mapper.discover_schema(conn_string)
                self.schema_info = self.schema_mapper.get_schema_for_ai()

                # Save to cache for future use
                self.schema_mapper._save_cache()

                print(f"✅ Esquema descubierto y guardado en cache")
            except Exception as e:
                self.logger.log_agent_activity(
                    "orchestrator",
                    "schema_discovery_error",
                    None,
                    f"Error discovering schema: {str(e)}"
                )
                print(f"⚠️ Error al descubrir esquema: {str(e)}")

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
        self.visualization_agent = VisualizationAgent()

        self.agents = {
            "interpreter": self.interpreter,
            "planner": self.planner,
            "executor": self.executor,
            "response": self.response_agent,
            "visualization": self.visualization_agent
        }

    def process_user_query(self, user_query: str, debug: bool = False) -> Dict[str, Any]:
        """
        Process a user query through the complete agent pipeline with task management

        Args:
            user_query: The user's natural language query
            debug: Whether to run in debug mode

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
            # Step 1: Interpret and validate the user query
            print("🔍 Interpretando y validando consulta...")
            self.logger.log_agent_activity("orchestrator", "starting_interpretation", workflow_data)
            interpretation_result = self.interpreter.process(workflow_data)

            # Log validation result (valid or rejected)
            is_valid = interpretation_result.get("valid", True)
            self.logger.log_agent_activity(
                "interpreter",
                "query_validated" if is_valid else "query_rejected",
                {"user_query": user_query, "valid": is_valid},
                interpretation_result
            )

            # Check if query was rejected by guardrails
            if interpretation_result.get("status") == "rejected":
                rejection_reason = interpretation_result.get("reason", "Consulta no válida")
                print(f"🚫 Consulta rechazada: {rejection_reason}")

                self.logger.log_agent_activity(
                    "orchestrator",
                    "workflow_terminated_rejection",
                    {"user_query": user_query, "reason": rejection_reason}
                )

                # Log rejected query completion
                self.logger.log_query_complete(success=False, error=f"Query rejected: {rejection_reason}")

                # Mensaje amigable para el usuario (sin revelar detalles de seguridad)
                user_message = self._get_rejection_message(rejection_reason)

                return {
                    "success": False,
                    "rejected": True,
                    "error": user_message,
                    "reason": rejection_reason,  # Para logs internos
                    "user_query": user_query,
                    "executive_response": "",
                    "final_response": "",
                    "agents_used": ["Interpreter"]
                }

            workflow_data.update(interpretation_result)
            print("✅ Consulta validada")

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

            # Step 5: Generate visualizations if applicable
            # Extract query results WITH metadata (separated, not combined)
            execution_results = workflow_data.get("execution_results", [])

            structured_results = []
            for i, result in enumerate(execution_results):
                if result.get("status") == "success" and isinstance(result.get("result"), str):
                    try:
                        parsed_result = json.loads(result["result"])
                        if parsed_result.get("success") and "data" in parsed_result:
                            data = parsed_result["data"]
                            if isinstance(data, list) and len(data) > 0:
                                structured_results.append({
                                    "description": result.get("description", result.get("task_description", f"Query {i+1}")),
                                    "data": data,
                                    "row_count": len(data),
                                    "columns": list(data[0].keys()) if data else [],
                                    "is_primary": False
                                })
                                print(f"   📊 Dataset {i+1}: '{structured_results[-1]['description']}' - {len(data)} filas")
                    except:
                        continue

            # Mark the last result as primary (final query answer)
            if structured_results:
                structured_results[-1]["is_primary"] = True
                print(f"   📊 Dataset primario: '{structured_results[-1]['description']}'")

            # Evaluate if visualization makes sense (use primary dataset for heuristics)
            primary_data = structured_results[-1]["data"] if structured_results else []
            should_visualize = self._should_generate_visualization(primary_data, user_query)

            if should_visualize:
                print("📊 Generando visualizaciones...")
                # Pass full context to visualization agent
                viz_input = {
                    "structured_results": structured_results,
                    "user_query": user_query,
                    "interpretation": workflow_data.get("interpretation", ""),
                    "executive_response": response_result.get("executive_response", "")
                }
                self.logger.log_agent_activity("orchestrator", "starting_visualization_generation", {"num_datasets": len(structured_results), "user_query": user_query})
                visualization_result = self.visualization_agent.process(viz_input)
                self.logger.log_agent_activity("visualization", "process_completed", {"num_datasets": len(structured_results)}, visualization_result)
                workflow_data.update(visualization_result)
            else:
                print("📊 Visualización omitida (no aporta valor según heurísticas)")
                self.logger.log_agent_activity("orchestrator", "visualization_skipped", {"reason": "heuristics", "user_query": user_query})

            # Debug file for workflow_data and execution_result if needed
            if debug:
                try:
                    # Use safe serialization for complex objects
                    workflow_debug_file = debug_workflow_data(workflow_data, user_query)
                    print(f"🐛 Debug workflow data saved to: {workflow_debug_file}")

                    # Also save execution result safely
                    from utils.debug_serializer import safe_json_dump
                    safe_json_dump(execution_result, "debug/execution_result_debug.json")
                    print(f"🐛 Debug execution result saved to: debug/execution_result_debug.json")

                except Exception as debug_error:
                    print(f"⚠️ Debug save failed: {debug_error}")
                    self.logger.log_error("debug_serialization", str(debug_error), {"workflow_data_keys": list(workflow_data.keys()) if isinstance(workflow_data, dict) else []})



            # Clean workflow_data before returning (remove non-serializable objects)
            clean_workflow = {k: v for k, v in workflow_data.items()
                            if k not in ('task_manager', 'schema_info') and not callable(v)}

            # Log successful query completion
            self.logger.log_query_complete(success=True)

            return {
                "success": True,
                "workflow_data": clean_workflow,
                "executive_response": response_result.get("executive_response", ""),
                "final_response": response_result.get("final_response", ""),
                "execution_summary": exec_summary,
                "agents_used": [agent.name for agent in self.agents.values()],
                "task_details": execution_result.get("task_manager_state", {})
            }

        except Exception as e:
            # Log failed query completion
            self.logger.log_query_complete(success=False, error=str(e))
            return {
                "success": False,
                "error": str(e)
            }

    def _get_rejection_message(self, reason: str) -> str:
        """
        Generate user-friendly rejection message.
        Always returns same friendly message with examples (reason is logged separately).
        """
        return (
            "Solo puedo responder consultas sobre datos forestales y de fauna silvestre de SERFOR. "
            "Por ejemplo: '¿Cuántos títulos habilitantes hay en Loreto?' o "
            "'¿Cuáles son las plantaciones registradas en Cusco?'"
        )

    def _should_generate_visualization(self, query_results: list, user_query: str) -> bool:
        """
        Heuristics to determine if visualization would add value.

        Returns False for cases where a chart wouldn't help:
        - Single value results (counts, sums, averages)
        - Very few rows with few columns
        - Simple list queries without comparable dimensions
        """
        if not query_results or len(query_results) == 0:
            return False

        num_rows = len(query_results)
        num_cols = len(query_results[0]) if query_results else 0

        # Case 1: Single row = single value result (e.g., "total: 523")
        if num_rows == 1:
            print(f"   → Heurística: 1 fila = valor único, no visualizar")
            return False

        # Case 2: Very few rows (2-3) with just 1-2 columns
        if num_rows <= 3 and num_cols <= 2:
            print(f"   → Heurística: {num_rows} filas x {num_cols} cols = muy pocos datos")
            return False

        # Case 3: Check if query is a simple count/sum question
        simple_query_patterns = [
            "cuántos", "cuantos", "cuántas", "cuantas",
            "total de", "suma de", "suma total",
            "cantidad de", "número de", "numero de"
        ]
        query_lower = user_query.lower()

        # If it's a simple count AND has few rows, skip
        if any(pattern in query_lower for pattern in simple_query_patterns) and num_rows <= 5:
            print(f"   → Heurística: consulta de conteo simple con {num_rows} filas")
            return False

        # Case 4: Minimum threshold - need at least 3 rows for meaningful visualization
        if num_rows < 3:
            print(f"   → Heurística: menos de 3 filas, insuficiente para visualizar")
            return False

        print(f"   → Heurística: {num_rows} filas x {num_cols} cols = proceder con visualización")
        return True

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