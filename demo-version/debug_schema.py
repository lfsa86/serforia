"""
Debug script to check schema discovery
"""
from database.connection_manager import DatabaseConnectionManager
import pyodbc

def main():
    print("🔍 Debug Schema Discovery")
    print("=" * 50)

    db_manager = DatabaseConnectionManager()

    print("📊 Connection config:")
    config = db_manager.get_connection_info()
    for key, value in config.items():
        print(f"  {key}: {value}")

    print(f"\n🔗 Connection string:")
    conn_str = db_manager.get_connection_string()
    print(f"  {conn_str}")

    try:
        print("\n🔍 Manual schema discovery:")
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            # Check what tables exist
            tables_query = """
            SELECT
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            AND TABLE_SCHEMA NOT IN ('sys', 'information_schema')
            ORDER BY TABLE_SCHEMA, TABLE_NAME
            """

            print("📋 Tables found:")
            tables = []
            for row in cursor.execute(tables_query):
                schema_name, table_name, table_type = row
                tables.append((schema_name, table_name))
                print(f"  - {schema_name}.{table_name}")

            # Check columns for each table
            for schema_name, table_name in tables:
                print(f"\n📝 Columns for {schema_name}.{table_name}:")

                columns_query = """
                SELECT
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                ORDER BY ORDINAL_POSITION
                """

                col_count = 0
                for row in cursor.execute(columns_query, schema_name, table_name):
                    col_name, data_type, is_nullable, max_length = row
                    col_count += 1
                    print(f"    {col_count}. {col_name} ({data_type}) - Nullable: {is_nullable}")

                print(f"  Total columns: {col_count}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()