"""
Schema Agent - Specializes in analyzing and enriching database schemas
"""
from typing import Dict, Any
from .base_agent import BaseAgent

class SchemaAgent(BaseAgent):
    """Agent specialized in understanding and enriching database schemas"""

    def __init__(self):
        super().__init__(
            name="Schema",
            role_setup="""Eres un agente especializado en análisis de esquemas de bases de datos, específicamente para sistemas forestales y de fauna silvestre de SERFOR (Perú).

Tu tarea es analizar estructuras de tablas y columnas para proporcionar descripciones claras y útiles que ayuden a otros agentes a entender los datos.

Cuando analices una tabla:
1. Examina los nombres de columnas y sus tipos de datos
2. Observa los valores de muestra para entender el contenido
3. Considera el contexto forestal/ambiental de SERFOR
4. Proporciona descripciones claras y específicas

Conocimiento del dominio:
- SERFOR: Servicio Nacional Forestal y de Fauna Silvestre de Perú
- Infracciones forestales: violaciones a normativas de aprovechamiento forestal
- Títulos habilitantes: permisos, concesiones, autorizaciones para actividades forestales
- OSINFOR: Organismo de Supervisión de los Recursos Forestales
- ATFFS: Administración Técnica Forestal y de Fauna Silvestre
- UIT: Unidad Impositiva Tributaria (para multas)
- UBIGEO: Código geográfico estándar del Perú

Responde SIEMPRE en formato JSON con:
- table_description: Descripción de la tabla
- column_descriptions: Objeto con descripción para cada columna""",
            temperature=0.2
        )

    def analyze_table_schema(self, table_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a table schema and provide enriched descriptions

        Args:
            table_info: Dictionary with table schema information

        Returns:
            Dictionary with enriched descriptions
        """
        prompt = f"""
        Analiza esta tabla de la base de datos SERFOR y proporciona descripciones detalladas:

        Nombre de tabla: {table_info.get('table_name', 'Unknown')}
        Número estimado de filas: {table_info.get('row_count', 'Unknown')}

        Columnas:
        {self._format_columns_for_analysis(table_info.get('columns', []))}

        Proporciona descripciones específicas y útiles que ayuden a entender:
        - Qué representa cada campo
        - Cómo se relaciona con procesos forestales/ambientales
        - Valores típicos o rangos esperados
        - Restricciones o formatos especiales

        Responde en formato JSON con table_description y column_descriptions.
        """

        response = self.run(prompt)

        return {
            "status": "analyzed",
            "table_name": table_info.get('table_name'),
            "enrichment_result": response,
            "agent": self.name
        }

    def suggest_query_patterns(self, table_schemas: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest common query patterns based on schema analysis

        Args:
            table_schemas: Dictionary with multiple table schemas

        Returns:
            Dictionary with suggested query patterns
        """
        prompt = f"""
        Basándote en estos esquemas de tablas de SERFOR, sugiere patrones de consulta comunes:

        {self._format_multiple_tables(table_schemas)}

        Proporciona en formato JSON:
        - common_queries: Lista de consultas típicas que los usuarios podrían hacer
        - relationships: Posibles relaciones entre tablas
        - aggregation_patterns: Patrones de agregación útiles
        - filtering_suggestions: Campos comunes para filtrar

        Enfócate en consultas útiles para análisis forestal y de fauna silvestre.
        """

        response = self.run(prompt)

        return {
            "status": "patterns_suggested",
            "suggestions": response,
            "agent": self.name
        }

    def validate_query_against_schema(self, query_intent: str, available_schemas: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate if a query intent can be satisfied with available schemas

        Args:
            query_intent: Natural language description of what user wants
            available_schemas: Available table schemas

        Returns:
            Validation result with suggestions
        """
        prompt = f"""
        Un usuario quiere hacer esta consulta: "{query_intent}"

        Esquemas disponibles:
        {self._format_multiple_tables(available_schemas)}

        Analiza si la consulta es posible y proporciona en JSON:
        - feasible: true/false si la consulta es realizable
        - required_tables: Tablas necesarias para la consulta
        - required_columns: Columnas específicas necesarias
        - suggested_approach: Enfoque recomendado para la consulta
        - limitations: Limitaciones o datos faltantes
        - alternative_queries: Consultas alternativas si la original no es posible
        """

        response = self.run(prompt)

        return {
            "status": "validated",
            "query_intent": query_intent,
            "validation_result": response,
            "agent": self.name
        }

    def _format_columns_for_analysis(self, columns: list) -> str:
        """Format columns for analysis prompt"""
        formatted = []
        for col in columns:
            samples_str = ", ".join(col.get('samples', [])[:3]) if col.get('samples') else "No samples"
            formatted.append(
                f"- {col.get('name', 'unknown')} ({col.get('type', 'unknown')}): "
                f"Nullable={col.get('nullable', 'unknown')}, "
                f"Samples=[{samples_str}]"
            )
        return "\n".join(formatted)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data using schema analysis (implements BaseAgent abstract method)

        Args:
            input_data: Dictionary with schema analysis request

        Returns:
            Dictionary with analysis results
        """
        if "table_info" in input_data:
            return self.analyze_table_schema(input_data["table_info"])
        elif "table_schemas" in input_data:
            return self.suggest_query_patterns(input_data["table_schemas"])
        elif "query_intent" in input_data and "available_schemas" in input_data:
            return self.validate_query_against_schema(
                input_data["query_intent"],
                input_data["available_schemas"]
            )
        else:
            return {
                "status": "error",
                "error": "Invalid input data for schema analysis",
                "agent": self.name
            }

    def _format_multiple_tables(self, tables: Dict[str, Any]) -> str:
        """Format multiple tables for analysis"""
        formatted = []
        for table_name, table_info in tables.items():
            formatted.append(f"\nTabla: {table_name}")
            formatted.append(f"Descripción: {table_info.get('description', 'No description')}")
            formatted.append("Columnas principales:")

            columns = table_info.get('columns', [])[:10]  # Limit to first 10 columns
            for col in columns:
                formatted.append(f"  - {col.get('name')} ({col.get('type')})")

            if len(table_info.get('columns', [])) > 10:
                formatted.append(f"  ... y {len(table_info.get('columns', [])) - 10} columnas más")

        return "\n".join(formatted)