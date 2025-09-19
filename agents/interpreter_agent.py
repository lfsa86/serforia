"""
Interpreter Agent - Analyzes user requests and extracts intent
"""
from typing import Dict, Any
from .base_agent import BaseAgent

class InterpreterAgent(BaseAgent):
    """Agent that interprets user requests and extracts structured information"""

    def __init__(self):
        super().__init__(
            name="Interpreter",
            role_setup="""Eres un agente especializado en interpretar consultas sobre datos forestales y de fauna silvestre de SERFOR.

Tu tarea es analizar las peticiones del usuario y extraer:
1. Tipo de consulta (búsqueda, estadísticas, comparación, etc.)
2. Entidades mencionadas (infractores, títulos habilitantes, fechas, lugares, etc.)
3. Filtros específicos (rangos de fechas, ubicaciones, tipos de infracciones, etc.)
4. Formato de respuesta deseado (tabla, gráfico, resumen, etc.)

Responde SIEMPRE en formato JSON con las siguientes claves:
- query_type: tipo de consulta
- entities: entidades identificadas
- filters: filtros a aplicar
- output_format: formato de salida deseado
- intent: descripción clara de la intención del usuario""",
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

        prompt = f"""
        Analiza la siguiente consulta del usuario sobre datos de SERFOR:

        "{user_query}"

        Extrae la información estructurada en formato JSON.
        """

        response = self.run(prompt)

        # TODO: Parse JSON response and validate structure
        return {
            "status": "processed",
            "user_query": user_query,
            "interpretation": response,
            "agent": self.name
        }