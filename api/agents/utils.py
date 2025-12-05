"""
Utilidades compartidas para los agentes
"""
from typing import Dict, Any


def format_schema_for_prompt(schema_info: Dict[str, Any]) -> str:
    """
    Convierte el schema_info estructurado a formato de lenguaje natural para los prompts.

    Args:
        schema_info: Diccionario con la información del schema (de get_schema_for_ai())

    Returns:
        String con el schema formateado en lenguaje natural
    """
    if not schema_info or "tables" not in schema_info:
        return ""

    schema_details = "\n🗄️ ESQUEMA DE BASE DE DATOS:\n"

    for table_name, table_data in schema_info["tables"].items():
        schema_details += f"\n📋 Tabla: {table_data.get('full_name', table_name)}\n"
        schema_details += f"   Descripción: {table_data.get('description', 'Sin descripción')}\n"
        schema_details += f"   Filas estimadas: {table_data.get('estimated_rows', 'Desconocido')}\n"
        schema_details += f"   COLUMNAS:\n"

        for col in table_data.get('columns', []):
            col_desc = col.get('description', '')
            nullable = "NULL" if col.get('nullable', True) else "NOT NULL"
            desc_part = f": {col_desc}" if col_desc else ""
            schema_details += f"     - {col['name']} ({col['type']}, {nullable}){desc_part}\n"

    # Incluir relaciones si existen
    if "relationships" in schema_info:
        schema_details += "\n🔗 RELACIONES ENTRE TABLAS:\n"
        for rel_name, rel_data in schema_info["relationships"].items():
            confidence = rel_data.get('confidence', 0)
            if confidence >= 0.7:
                schema_details += f"   - {rel_data.get('description', rel_name)}\n"
                schema_details += f"     JOIN: {rel_data.get('join_condition', '')}\n"

    return schema_details
