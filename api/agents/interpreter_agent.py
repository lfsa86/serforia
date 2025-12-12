"""
Interpreter Agent - Analyzes user requests and extracts intent
"""
from typing import Dict, Any
import json
import re
from .base_agent import BaseAgent
from .prompts.interpreter_prompt import ROLE_SETUP, INTERPRETATION_PROMPT_TEMPLATE


class InterpreterAgent(BaseAgent):
    """Agent that interprets user requests and extracts structured information"""

    def __init__(self):
        super().__init__(
            name="Interpreter",
            role_setup=ROLE_SETUP,
            temperature=0.2
        )

    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response by removing markdown and other unwanted characters"""
        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        response = response.strip()

        # Find JSON content between first { and last }
        start_idx = response.find('{')
        end_idx = response.rfind('}')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            response = response[start_idx:end_idx + 1]

        return response

    def _parse_interpretation(self, response: str) -> Dict[str, Any]:
        """Parse the JSON response from the LLM"""
        try:
            cleaned = self._clean_json_response(response)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Si no se puede parsear, asumir que es válida pero devolver el raw
            return {
                "valid": True,
                "reason": None,
                "interpretation": {"raw": response}
            }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request and extract structured intent

        Args:
            input_data: Dictionary with 'user_query' key

        Returns:
            Dictionary with extracted intent information
        """
        user_query = input_data.get("user_query", "")

        prompt = INTERPRETATION_PROMPT_TEMPLATE.format(
            user_query=user_query
        )

        response = self.run(prompt)

        # Parse the JSON response
        parsed = self._parse_interpretation(response)
        is_valid = parsed.get("valid", True)

        if is_valid:
            return {
                "status": "validated",
                "valid": True,
                "user_query": user_query,
                "entities": parsed.get("entities", []),
                "interpretation": parsed.get("interpretation", ""),
                "agent": self.name
            }
        else:
            return {
                "status": "rejected",
                "valid": False,
                "user_query": user_query,
                "reason": parsed.get("reason", "Consulta no válida"),
                "interpretation": None,
                "agent": self.name
            }