"""
Service layer for orchestrator functionality
"""
import sys
import os
from typing import Dict, Any, List
import json

# Add parent directories to path to import agents
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))

from agents.orchestrator import AgentOrchestrator
from utils.logger import init_logger


class OrchestratorService:
    """Service to manage the agent orchestrator"""

    def __init__(self):
        """Initialize the orchestrator service"""
        self.logger = init_logger()
        self.orchestrator = AgentOrchestrator()
        print("✅ OrchestratorService initialized")

    def process_query(self, query: str, include_workflow: bool = False) -> Dict[str, Any]:
        """
        Process a user query through the orchestrator

        Args:
            query: User's natural language query
            include_workflow: Whether to include detailed workflow data

        Returns:
            Dictionary with query results
        """
        try:
            self.logger.log_user_query(query)

            # Process through orchestrator
            result = self.orchestrator.process_user_query(query, include_workflow)

            print(f"🔍 DEBUG - Result from orchestrator: success={result.get('success')}, has final_response={('final_response' in result)}")
            print(f"🔍 DEBUG - Result keys: {list(result.keys())}")

            # Ensure final_response is ALWAYS present first
            if "final_response" not in result:
                result["final_response"] = result.get("error", "")
                print(f"🔍 DEBUG - Added final_response from error: '{result['final_response']}'")

            if not result.get("success"):
                self.logger.log_error("OrchestratorService", f"Query processing failed: {result.get('error')}")
                print(f"🔍 DEBUG - Returning error result: {result}")
                return result

            # Extract and format data for API response
            response_data = {
                "success": True,
                "final_response": result.get("final_response", ""),
                "agents_used": result.get("agents_used", []),
            }

            # Extract table data if available
            workflow_data = result.get("workflow_data", {})
            execution_results = workflow_data.get("execution_results", [])

            table_data = self._extract_table_data(execution_results)
            if table_data:
                response_data["data"] = table_data

            # Extract SQL queries
            sql_queries = self._extract_sql_queries(execution_results)
            if sql_queries:
                response_data["sql_queries"] = sql_queries

            # Extract visualization data (Plotly JSON)
            viz_data = workflow_data.get("visualization_data", [])
            if viz_data:
                response_data["visualization_data"] = viz_data
                print(f"📊 DEBUG - Visualization data extracted: {len(viz_data)} visualizations")

            # Include workflow data if requested
            if include_workflow:
                response_data["workflow_data"] = workflow_data

            self.logger.log_agent_activity(
                "OrchestratorService",
                "query_completed",
                None,
                f"Agents used: {response_data['agents_used']}"
            )
            return response_data

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ ERROR in OrchestratorService:")
            print(error_detail)
            self.logger.log_error("OrchestratorService", f"Error processing query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "final_response": f"Error processing query: {str(e)}",
                "agents_used": []
            }

    def _extract_table_data(self, execution_results: List[Dict]) -> List[Dict]:
        """Extract table data from execution results"""
        for result in execution_results:
            if result.get("status") == "success" and isinstance(result.get("result"), str):
                try:
                    parsed_result = json.loads(result["result"])
                    print(f"🔍 DEBUG - Parsed result: {parsed_result}")
                    if parsed_result.get("success") and "data" in parsed_result:
                        data = parsed_result["data"]
                        print(f"📊 DEBUG - Data extracted: {len(data)} rows")
                        if isinstance(data, list) and len(data) > 0:
                            return data
                except Exception as e:
                    print(f"❌ DEBUG - Error parsing result: {e}")
                    continue
        return None

    def _extract_sql_queries(self, execution_results: List[Dict]) -> List[Dict]:
        """Extract SQL queries from execution results"""
        sql_queries = []

        for result in execution_results:
            if result.get("status") == "success" and isinstance(result.get("result"), str):
                try:
                    parsed_result = json.loads(result["result"])
                    if "query_executed" in parsed_result:
                        sql_queries.append({
                            "query": parsed_result["query_executed"],
                            "success": parsed_result.get("success", False),
                            "row_count": parsed_result.get("row_count", 0),
                            "task_description": result.get("task_description", "SQL Query")
                        })
                    elif "query_attempted" in parsed_result:
                        sql_queries.append({
                            "query": parsed_result["query_attempted"],
                            "success": False,
                            "error": parsed_result.get("error", "Unknown error"),
                            "task_description": result.get("task_description", "SQL Query")
                        })
                except Exception:
                    continue

        return sql_queries if sql_queries else None


# Global instance (singleton pattern)
_orchestrator_service = None


def get_orchestrator_service() -> OrchestratorService:
    """Get or create the orchestrator service instance"""
    global _orchestrator_service
    if _orchestrator_service is None:
        _orchestrator_service = OrchestratorService()
    return _orchestrator_service
