from database.schema_mapper import DynamicSchemaMapper

schema_mapper = DynamicSchemaMapper()
schema_info = schema_mapper.get_schema_for_ai()

schema_details = ""
if schema_info and "tables" in schema_info:
    schema_details = "\n🗄️ ESQUEMA COMPLETO DE BASE DE DATOS:\n"
    for table_name, table_data in schema_info["tables"].items():
        schema_details += f"\n📋 Tabla: {table_data.get('full_name', table_name)}\n"
        schema_details += f"   Descripción: {table_data.get('description', 'Sin descripción')}\n"
        schema_details += f"   Filas estimadas: {table_data.get('estimated_rows', 'Desconocido')}\n"
        schema_details += f"   TODAS LAS COLUMNAS:\n"

        # Include ALL columns with full details
        for col in table_data.get('columns', []):
            col_desc = col.get('description', 'Sin descripción')
            nullable = "NULL" if col.get('nullable', True) else "NOT NULL"
            schema_details += f"     - {col['name']} ({col['type']}, {nullable}): {col_desc}\n"

if schema_info and "relationships" in schema_info:
    schema_details += "\n\n🔗 RELACIONES ENTRE TABLAS:\n"
    schema_details += "Estas son las formas validadas de unir las tablas mediante JOINs:\n\n"

    for rel_name, rel_data in schema_info["relationships"].items():
        # Only include high confidence relationships
        confidence = rel_data.get('confidence', 0)
        if confidence >= 0.7:
            schema_details += f"     - {rel_data.get('description', rel_name)}\n"
            schema_details += f"        JOIN: {rel_data.get('join_condition', '')}\n\n"
            #schema_details += f"     Confianza: {confidence:.0%}, "
            #schema_details += f"Valores compartidos: {rel_data.get('shared_values_count', 0)}\n\n"

print(schema_details)