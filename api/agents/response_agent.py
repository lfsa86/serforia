"""
Response Agent - Formats and presents final results to the user
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from .prompts.response_prompt import ROLE_SETUP, RESPONSE_PROMPT_TEMPLATE
import json
import re
import pandas as pd
from collections import Counter

class ResponseAgent(BaseAgent):
    """Agent that formats execution results into user-friendly responses"""

    def __init__(self):
        super().__init__(
            name="Response",
            role_setup=ROLE_SETUP,
            temperature=0.5
        )

    def _generate_data_summary(self, data: List[Dict], task_description: str = "Query") -> Dict[str, Any]:
        """
        Generate an intelligent statistical summary of the data.
        This allows the LLM to understand the data without needing all rows.
        """
        if not data:
            return {"task": task_description, "empty": True}

        df = pd.DataFrame(data)
        summary = {
            "task": task_description,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "column_analysis": {}
        }

        for col in df.columns:
            col_data = df[col].dropna()
            col_info = {
                "null_count": int(df[col].isna().sum()),
                "unique_count": int(df[col].nunique())
            }

            # Detect column type and generate appropriate stats
            if pd.api.types.is_numeric_dtype(col_data):
                # Numeric column: min, max, mean, sum
                col_info["type"] = "numeric"
                col_info["min"] = float(col_data.min()) if len(col_data) > 0 else None
                col_info["max"] = float(col_data.max()) if len(col_data) > 0 else None
                col_info["mean"] = round(float(col_data.mean()), 2) if len(col_data) > 0 else None
                col_info["sum"] = float(col_data.sum()) if len(col_data) > 0 else None

            elif pd.api.types.is_datetime64_any_dtype(col_data):
                # Date column: range
                col_info["type"] = "date"
                col_info["min_date"] = str(col_data.min()) if len(col_data) > 0 else None
                col_info["max_date"] = str(col_data.max()) if len(col_data) > 0 else None

            else:
                # Categorical/text column: top values distribution
                col_info["type"] = "categorical"
                if col_info["unique_count"] <= 20:
                    # Show full distribution if few unique values
                    value_counts = col_data.value_counts().head(10).to_dict()
                    col_info["distribution"] = {str(k): int(v) for k, v in value_counts.items()}
                else:
                    # Show top 5 for high cardinality
                    value_counts = col_data.value_counts().head(5).to_dict()
                    col_info["top_values"] = {str(k): int(v) for k, v in value_counts.items()}
                    col_info["sample_values"] = [str(v) for v in col_data.head(3).tolist()]

            summary["column_analysis"][col] = col_info

        return summary

    def _summarize_execution_results(self, execution_results: List[Dict]) -> str:
        """
        Generate intelligent summaries of all execution results.
        """
        if not execution_results:
            return "No hay resultados de ejecución."

        summaries = []
        for result in execution_results:
            if result.get("status") == "success" and isinstance(result.get("result"), str):
                try:
                    parsed = json.loads(result["result"])
                    if parsed.get("success") and "data" in parsed:
                        data = parsed["data"]
                        task_desc = result.get("description", "Query")
                        summary = self._generate_data_summary(data, task_desc)
                        summaries.append(summary)
                except Exception as e:
                    summaries.append({
                        "task": result.get("description", "Query"),
                        "error": f"Error parsing: {str(e)}"
                    })
            elif result.get("status") == "failed":
                summaries.append({
                    "task": result.get("description", "Query"),
                    "error": result.get("error", "Unknown error")
                })

        return json.dumps(summaries, ensure_ascii=False, indent=2)

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
        execution_results = input_data.get("execution_results", [])
        user_query = input_data.get("user_query", "")
        interpretation = input_data.get("interpretation", "")

        # Generate intelligent summary instead of passing all data
        summarized_results = self._summarize_execution_results(execution_results)

        print(f"📊 ResponseAgent - Data summary generated ({len(summarized_results)} chars)")

        prompt = RESPONSE_PROMPT_TEMPLATE.format(
            user_query=user_query,
            interpretation=interpretation,
            execution_results=summarized_results
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