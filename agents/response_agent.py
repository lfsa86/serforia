"""
Response Agent - Formats and presents final results to the user
"""
from typing import Dict, Any
from .base_agent import BaseAgent

class ResponseAgent(BaseAgent):
    """Agent that formats execution results into user-friendly responses"""

    def __init__(self):
        super().__init__(
            name="Response",
            role_setup="""Eres un agente especializado en formatear y presentar resultados de consultas sobre datos de SERFOR de manera clara y comprensible.

Tu tarea es tomar los resultados de las consultas ejecutadas y crear respuestas que:
1. Sean fáciles de entender para el usuario
2. Estén bien estructuradas y organizadas
3. Incluyan el formato solicitado (tablas, gráficos, resúmenes, etc.)
4. Proporcionen contexto relevante sobre los datos
5. Incluyan interpretaciones y insights cuando sea apropiado

Puedes crear:
- Tablas en formato markdown
- Resúmenes ejecutivos
- Listas organizadas
- Explicaciones contextuales
- Recomendaciones basadas en los datos

Siempre mantén un tono profesional pero accesible.""",
            temperature=0.5
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format execution results into user-friendly response

        Args:
            input_data: Dictionary with execution results

        Returns:
            Dictionary with formatted response
        """
        execution_results = input_data.get("execution_results", "")
        user_query = input_data.get("user_query", "")
        interpretation = input_data.get("interpretation", "")

        prompt = f"""
        Basándote en los siguientes datos:

        Consulta original del usuario: "{user_query}"

        Interpretación: {interpretation}

        Resultados de ejecución: {execution_results}

        Crea una respuesta clara, bien estructurada y comprensible para el usuario.
        Incluye contexto relevante y presenta la información de la manera más útil posible.
        """

        response = self.run(prompt)

        return {
            "status": "completed",
            "user_query": user_query,
            "final_response": response,
            "agent": self.name
        }