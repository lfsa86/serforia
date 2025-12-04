"""
Response Agent - Formats and presents final results to the user
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from .prompts.response_prompt import ROLE_SETUP, RESPONSE_PROMPT_TEMPLATE
import json
import re

class ResponseAgent(BaseAgent):
    """Agent that formats execution results into user-friendly responses"""

    def __init__(self):
        super().__init__(
            name="Response",
            role_setup=ROLE_SETUP,
            temperature=0.5
        )

    def _parse_tagged_response(self, response: str) -> Dict[str, str]:
        """
        Parse response with tags to extract executive and insight responses.

        Args:
            response: Raw response with <executive_res> and <insight_res> tags

        Returns:
            Dictionary with 'executive' and 'insight' keys
        """
        executive = ""
        insight = ""

        # Extract executive response
        exec_match = re.search(r'<executive_res>(.*?)</executive_res>', response, re.DOTALL)
        if exec_match:
            executive = exec_match.group(1).strip()

        # Extract insight response - try with closing tag first
        insight_match = re.search(r'<insight_res>(.*?)</insight_res>', response, re.DOTALL)
        if insight_match:
            insight = insight_match.group(1).strip()
        else:
            # If no closing tag, get everything after <insight_res>
            insight_match = re.search(r'<insight_res>(.*)', response, re.DOTALL)
            if insight_match:
                insight = insight_match.group(1).strip()

        # Fallback: if no tags found, use full response as insight
        if not executive and not insight:
            insight = response.strip()

        return {
            "executive": executive,
            "insight": insight
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format execution results into user-friendly response

        Args:
            input_data: Dictionary with execution results

        Returns:
            Dictionary with executive_response and final_response (detailed)
        """
        execution_results = input_data.get("execution_results", "")
        user_query = input_data.get("user_query", "")
        interpretation = input_data.get("interpretation", "")

        prompt = RESPONSE_PROMPT_TEMPLATE.format(
            user_query=user_query,
            interpretation=interpretation,
            execution_results=execution_results
        )

        response = self.run(prompt)

        print(f"\n{'='*60}")
        print("🔍 DEBUG ResponseAgent - Raw response from LLM:")
        print(f"{'='*60}")
        print(response)
        print(f"{'='*60}\n")

        parsed = self._parse_tagged_response(response)

        print(f"📋 DEBUG ResponseAgent - Parsed executive_response:")
        print(f"   Length: {len(parsed['executive'])} chars")
        print(f"   Content: {parsed['executive'][:200]}..." if len(parsed['executive']) > 200 else f"   Content: {parsed['executive']}")
        print(f"\n📋 DEBUG ResponseAgent - Parsed insight (final_response):")
        print(f"   Length: {len(parsed['insight'])} chars")
        print(f"   Content: {parsed['insight'][:200]}..." if len(parsed['insight']) > 200 else f"   Content: {parsed['insight']}")
        print(f"{'='*60}\n")

        return {
            "status": "completed",
            "user_query": user_query,
            "executive_response": parsed["executive"],
            "final_response": parsed["insight"],
            "agent": self.name
        }