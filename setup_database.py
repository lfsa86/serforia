"""
Database Setup Script - Discovers schema and enriches with AI descriptions
"""
from database.schema_mapper import DynamicSchemaMapper
from database.connection_manager import DatabaseConnectionManager
from agents.schema_agent import SchemaAgent
from dotenv import load_dotenv
import json

def main():
    """Setup and enrich database schema information"""
    print("🚀 SERFOR Database Setup")
    print("=" * 50)

    # Load environment variables
    load_dotenv()

    # Initialize components
    print("📡 Inicializando componentes...")
    db_manager = DatabaseConnectionManager()
    schema_mapper = DynamicSchemaMapper()
    schema_agent = SchemaAgent()

    # Test connection
    print("\n🔗 Probando conexión a base de datos...")
    connection_test = db_manager.test_connection()

    if not connection_test["success"]:
        print(f"❌ Error de conexión: {connection_test['error']}")
        print("\n💡 Verifica que:")
        print("- El contenedor Docker esté ejecutándose")
        print("- Las credenciales sean correctas")
        print("- El puerto 1433 esté disponible")
        return

    print("✅ Conexión exitosa")

    # Discover schema
    print("\n🔍 Descubriendo esquema de base de datos...")
    try:
        schema_mapper.set_connection_config(db_manager.connection_config)
        discovered_tables = schema_mapper.discover_schema()

        print(f"✅ Descubiertas {len(discovered_tables)} tablas:")
        for table_name, table_info in discovered_tables.items():
            print(f"   - {table_info.schema}.{table_name} ({len(table_info.columns)} columnas, ~{table_info.row_count_estimate} filas)")

    except Exception as e:
        print(f"❌ Error descubriendo esquema: {e}")
        return

    # Enrich with AI descriptions
    print("\n🧠 Enriqueciendo esquema con descripciones IA...")
    try:
        enriched_tables = schema_mapper.enrich_with_ai_descriptions(schema_agent)

        print("✅ Enriquecimiento completado:")
        for table_name, table_info in enriched_tables.items():
            if table_info.ai_enriched:
                print(f"   - {table_name}: {table_info.description[:60]}...")

    except Exception as e:
        print(f"⚠️ Error en enriquecimiento IA: {e}")
        print("Continuando con esquema básico...")

    # Show final schema summary
    print("\n📊 Resumen final del esquema:")
    schema_info = schema_mapper.get_schema_for_ai()

    for table_name, table_data in schema_info["tables"].items():
        print(f"\n📋 Tabla: {table_data['full_name']}")
        print(f"   Descripción: {table_data.get('description', 'Sin descripción')}")
        print(f"   Filas estimadas: {table_data.get('estimated_rows', 'Desconocido')}")
        print(f"   Columnas: {len(table_data.get('columns', []))}")

        # Show first few columns
        columns = table_data.get('columns', [])[:5]
        for col in columns:
            desc = col.get('description', 'Sin descripción')[:40]
            print(f"     - {col['name']} ({col['type']}): {desc}...")

        if len(table_data.get('columns', [])) > 5:
            print(f"     ... y {len(table_data.get('columns', [])) - 5} columnas más")

    # Test some basic queries
    print("\n🧪 Probando consultas básicas...")
    test_queries = [
        ("Conteo de infractores", "SELECT COUNT(*) as total FROM Dir.T_GEP_INFRACTORES"),
        ("Conteo de títulos", "SELECT COUNT(*) as total FROM Dir.T_GEP_TITULOHABILITANTE"),
        ("Muestra de infractores", "SELECT TOP 3 TX_Infractor, TX_AmbitoInfraccion FROM Dir.T_GEP_INFRACTORES WHERE TX_Infractor IS NOT NULL")
    ]

    for test_name, query in test_queries:
        try:
            result = db_manager.execute_query(query)
            if result["success"]:
                print(f"✅ {test_name}: {len(result['data'])} resultados")
            else:
                print(f"❌ {test_name}: {result['error']}")
        except Exception as e:
            print(f"❌ {test_name}: Error - {e}")

    print("\n🎉 Setup completado!")
    print("\nAhora puedes usar el sistema multi-agente con:")
    print("python main_agents.py")

    # Save configuration summary
    config_summary = {
        "setup_completed": True,
        "tables_discovered": len(discovered_tables),
        "connection_config": db_manager.get_connection_info(),
        "schema_location": schema_mapper.cache_file
    }

    with open("database/setup_summary.json", "w") as f:
        json.dump(config_summary, f, indent=2)

    print(f"\n📄 Resumen guardado en: database/setup_summary.json")

if __name__ == "__main__":
    main()