"""
Interpreter Agent - Analyzes user requests and extracts intent
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from .prompts.interpreter_prompt import ROLE_SETUP, INTERPRETATION_PROMPT_TEMPLATE
from .utils import format_schema_for_prompt

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

        # Format schema using shared utility
        schema_details = format_schema_for_prompt(schema_info)

        prompt = INTERPRETATION_PROMPT_TEMPLATE.format(
            user_query=user_query,
            schema_info=schema_details
        )

        response = self.run(prompt)

        # TODO: Parse JSON response and validate structure
        return {
            "status": "processed",
            "user_query": user_query,
            "interpretation": response,
            "agent": self.name
        }