"""
Response Agent - Formats and presents final results to the user
"""
from typing import Dict, Any
from .base_agent import BaseAgent
import json

class ResponseAgent(BaseAgent):
    """Agent that formats execution results into user-friendly responses"""

    def __init__(self):
        super().__init__(
            name="Response",
            role_setup="""Eres un agente especializado en formatear y presentar resultados de consultas sobre datos de SERFOR de manera clara y comprensible.

Tu tarea es analizar y presentar los resultados de consultas sobre datos forestales de manera clara y profesional.

OBJETIVOS PRINCIPALES:
1. Presentar los datos de forma clara y bien estructurada
2. Realizar análisis e insights basados en los resultados obtenidos
3. Proporcionar contexto relevante sobre los hallazgos
4. Formatear tablas y datos de manera legible
5. Identificar patrones, tendencias o datos destacables

FORMATOS A USAR:
- Tablas en formato markdown con datos organizados
- Resúmenes analíticos con insights
- Estadísticas clave y métricas relevantes
- Análisis de patrones en los datos
- Interpretaciones basadas en evidencia

LO QUE NO DEBES HACER:
- NO dar recomendaciones operativas o de gestión
- NO sugerir acciones específicas a tomar
- NO hacer predicciones o proyecciones
- NO opinar sobre políticas o decisiones institucionales

ENFOQUE: Ser un analista de datos objetivo que presenta hallazgos de manera clara y profesional.""",
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