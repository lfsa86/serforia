"""
Interpreter Agent - Analyzes user requests and extracts intent
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from .prompts.interpreter_prompt import ROLE_SETUP, INTERPRETATION_PROMPT_TEMPLATE

class InterpreterAgent(BaseAgent):
    """Agent that interprets user requests and extracts structured information"""

    def __init__(self):
        super().__init__(
            name="Interpreter",
            role_setup=ROLE_SETUP,
            temperature=0.1
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request and extract structured intent

        Args:
            input_data: Dictionary with 'user_query' key

        Returns:
            Dictionary with extracted intent information
        """
        user_query = input_data.get("user_query", "")
        schema_info = input_data.get("schema_info", {})

        # Format complete schema information for the prompt
        tables_summary = ""
        if schema_info and "tables" in schema_info:
            tables_summary = "\nEsquema completo de base de datos:\n"
            for table_name, table_data in schema_info["tables"].items():
                tables_summary += f"\n📋 Tabla: {table_data.get('full_name', table_name)}\n"
                tables_summary += f"   Descripción: {table_data.get('description', 'Sin descripción')}\n"
                tables_summary += f"   Filas estimadas: {table_data.get('estimated_rows', 'Desconocido')}\n"
                tables_summary += f"   Columnas (TODAS):\n"

                # Include ALL columns with descriptions
                for col in table_data.get("columns", []):
                    col_desc = col.get('description', 'Sin descripción')
                    tables_summary += f"     - {col['name']} ({col['type']}): {col_desc}\n"

        prompt = INTERPRETATION_PROMPT_TEMPLATE.format(
            user_query=user_query,
            schema_info=tables_summary
        )

        response = self.run(prompt)

        # TODO: Parse JSON response and validate structure
        return {
            "status": "processed",
            "user_query": user_query,
            "interpretation": response,
            "agent": self.name
        }