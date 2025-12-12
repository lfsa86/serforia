"""
Utilidades compartidas para los agentes
"""
from typing import Dict, Any


def format_schema_for_prompt(schema_info: Dict[str, Any]) -> str:
    """
    Convierte el schema_info estructurado a formato compacto para los prompts.

    Las descripciones detalladas de cada vista están en domain_knowledge.py,
    aquí solo mostramos las columnas técnicas para que el modelo genere queries correctas.

    Args:
        schema_info: Diccionario con la información del schema (de get_schema_for_ai())

    Returns:
        String con el schema formateado de forma compacta
    """
    if not schema_info or "tables" not in schema_info:
        return ""

    schema_details = "\n🗄️ COLUMNAS DE CADA VISTA:\n"

    for table_name, table_data in schema_info["tables"].items():
        full_name = table_data.get('full_name', table_name)
        rows = table_data.get('estimated_rows', '?')

        # Formato compacto: nombre(tipo) separados por coma
        cols = table_data.get('columns', [])
        col_list = [f"{c['name']}({c['type']})" for c in cols]

        schema_details += f"\n{full_name} ({rows} filas):\n"
        schema_details += f"  {', '.join(col_list)}\n"

    # NOTA: Las descripciones conceptuales y relaciones están en domain_knowledge.py

    return schema_details
