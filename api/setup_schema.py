#!/usr/bin/env python3
"""
Schema Setup Script - Discovers database schema and enriches with AI descriptions

Usage:
    cd api
    uv run python setup_schema.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.schema_mapper import DynamicSchemaMapper
from database.connection_manager import DatabaseConnectionManager
from agents.schema_agent import SchemaAgent
from dotenv import load_dotenv


def main():
    print("🚀 SERFOR Schema Setup")
    print("=" * 60)

    load_dotenv()

    # Test DB connection
    print("\n🔗 Probando conexión a base de datos...")
    db_manager = DatabaseConnectionManager()
    connection_test = db_manager.test_connection()

    if not connection_test["success"]:
        print(f"❌ Error de conexión: {connection_test['error']}")
        return

    print("✅ Conexión exitosa")

    # Discover schema
    print("\n🔍 Descubriendo esquema...")
    schema_mapper = DynamicSchemaMapper(cache_file="database/schema_cache.json")
    schema_mapper.set_connection_config(db_manager.connection_config)
    discovered_tables = schema_mapper.discover_schema()

    print(f"\n✅ Descubiertas {len(discovered_tables)} vistas")

    # Enrich with AI
    print("\n🧠 Enriqueciendo con IA...")
    schema_agent = SchemaAgent()
    enriched_tables = schema_mapper.enrich_with_ai_descriptions(schema_agent)

    # Show results
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)

    for table_name, table_info in enriched_tables.items():
        print(f"\n📋 {table_info.schema}.{table_name}")
        print(f"   Descripción: {table_info.description}")
        print(f"   Columnas con descripción:")
        for col in table_info.columns[:5]:
            if col.description:
                print(f"     - {col.name}: {col.description[:60]}...")

    print(f"\n📁 Guardado en: database/schema_cache.json")
    print("🎉 Completado!")


if __name__ == "__main__":
    main()
