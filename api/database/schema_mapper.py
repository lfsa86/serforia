"""
Dynamic Database Schema Mapper - Automatically discovers and maps database schemas
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ColumnInfo:
    """Information about a database column"""
    name: str
    data_type: str
    is_nullable: bool
    max_length: Optional[int] = None
    description: str = ""
    sample_values: List[str] = None
    constraints: List[str] = None
    ai_enriched: bool = False

    def __post_init__(self):
        if self.sample_values is None:
            self.sample_values = []
        if self.constraints is None:
            self.constraints = []

@dataclass
class TableInfo:
    """Information about a database table"""
    name: str
    schema: str
    description: str = ""
    columns: List[ColumnInfo] = None
    primary_keys: List[str] = None
    foreign_keys: Dict[str, str] = None
    indexes: List[str] = None
    row_count_estimate: Optional[int] = None
    ai_enriched: bool = False
    last_updated: str = ""

    def __post_init__(self):
        if self.columns is None:
            self.columns = []
        if self.primary_keys is None:
            self.primary_keys = []
        if self.foreign_keys is None:
            self.foreign_keys = {}
        if self.indexes is None:
            self.indexes = []
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

class DynamicSchemaMapper:
    """Dynamically discovers and maps database schemas"""

    def __init__(self, cache_file: str = "database/schema_cache.json"):
        self.cache_file = cache_file
        self.tables: Dict[str, TableInfo] = {}
        self.connection_config = self._load_default_config()
        self._load_cache()

        # Auto-discover if no cache exists
        if not self.tables:
            try:
                self.discover_schema()
            except Exception as e:
                print(f"Auto-discovery failed: {e}")

    def _load_default_config(self) -> Dict[str, str]:
        """Load default connection configuration from environment"""
        return {
            "server": os.getenv("DB_SERVER", "localhost"),
            "port": os.getenv("DB_PORT", "1433"),
            "database": os.getenv("DB_DATABASE", "SERFOR_BDDWH"),
            "username": os.getenv("DB_USERNAME", "sa"),
            "password": os.getenv("DB_PASSWORD", "SerforDB@2025"),
            "driver": os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
            "trust_certificate": os.getenv("DB_TRUST_CERT", "yes")
        }

    def set_connection_config(self, config: Dict[str, Any]):
        """Set database connection configuration"""
        self.connection_config = config

    def discover_schema(self, connection_string: str = None) -> Dict[str, TableInfo]:
        """
        Automatically discover database schema from live connection

        Args:
            connection_string: Optional connection string override

        Returns:
            Dictionary of discovered tables
        """
        if not connection_string and not self.connection_config:
            raise ValueError("No connection configuration provided")

        # Import here to avoid dependency issues if not needed
        try:
            import pyodbc
        except ImportError:
            raise ImportError("pyodbc required for schema discovery. Install with: pip install pyodbc")

        discovered_tables = {}

        try:
            # Use provided connection string or build from config
            if connection_string:
                conn_str = connection_string
            else:
                conn_str = self._build_connection_string()

            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()

                # Discover tables and views
                tables_query = """
                SELECT
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'VIEW'
                AND TABLE_SCHEMA NOT IN ('sys', 'information_schema')
                ORDER BY TABLE_SCHEMA, TABLE_NAME
                """

                # Use fetchall to get all tables first
                table_rows = cursor.execute(tables_query).fetchall()

                for row in table_rows:
                    schema_name, table_name, table_type = row

                    print(f"  Processing table: {schema_name}.{table_name}")

                    # Discover columns for this table
                    columns = self._discover_table_columns(cursor, schema_name, table_name)

                    # Get row count estimate
                    row_count = self._get_row_count_estimate(cursor, schema_name, table_name)

                    # Create table info
                    table_info = TableInfo(
                        name=table_name,
                        schema=schema_name,
                        columns=columns,
                        row_count_estimate=row_count,
                        last_updated=datetime.now().isoformat()
                    )

                    discovered_tables[table_name] = table_info

        except Exception as e:
            print(f"Error discovering schema: {e}")
            # Fall back to cached data if available
            return self.tables

        # Update internal tables and cache
        self.tables.update(discovered_tables)
        self._save_cache()

        return discovered_tables

    def _discover_table_columns(self, cursor, schema_name: str, table_name: str) -> List[ColumnInfo]:
        """Discover columns for a specific table"""
        columns = []

        columns_query = """
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """

        try:
            # Use fetchall to avoid cursor iteration issues
            rows = cursor.execute(columns_query, schema_name, table_name).fetchall()

            for row in rows:
                col_name, data_type, is_nullable, max_length, precision, scale = row

                # Get sample values for this column (limit to avoid long processing)
                samples = self._get_sample_values(cursor, schema_name, table_name, col_name, limit=3)

                column_info = ColumnInfo(
                    name=col_name,
                    data_type=data_type,
                    is_nullable=(is_nullable == 'YES'),
                    max_length=max_length,
                    sample_values=samples
                )

                columns.append(column_info)

            print(f"  Discovered {len(columns)} columns for {schema_name}.{table_name}")

        except Exception as e:
            print(f"  Error discovering columns for {schema_name}.{table_name}: {e}")

        return columns

    def _get_sample_values(self, cursor, schema_name: str, table_name: str, column_name: str, limit: int = 5) -> List[str]:
        """Get sample values from a column"""
        try:
            sample_query = f"""
            SELECT DISTINCT TOP {limit} [{column_name}]
            FROM [{schema_name}].[{table_name}]
            WHERE [{column_name}] IS NOT NULL
            ORDER BY [{column_name}]
            """

            samples = []
            for row in cursor.execute(sample_query):
                value = str(row[0]) if row[0] is not None else None
                if value and len(value) < 100:  # Avoid very long values
                    samples.append(value)

            return samples

        except Exception:
            return []

    def _get_row_count_estimate(self, cursor, schema_name: str, table_name: str) -> Optional[int]:
        """Get estimated row count for a table"""
        try:
            count_query = f"SELECT COUNT(*) FROM [{schema_name}].[{table_name}]"
            result = cursor.execute(count_query).fetchone()
            return result[0] if result else None
        except Exception:
            return None

    def _build_connection_string(self) -> str:
        """Build connection string from config"""
        if not self.connection_config:
            raise ValueError("No connection configuration available")

        # Build SQL Server connection string
        parts = []

        # Server with port
        server_part = self.connection_config.get('server', 'localhost')
        port = self.connection_config.get('port', '1433')
        parts.append(f"Server={server_part},{port}")

        if 'database' in self.connection_config:
            parts.append(f"Database={self.connection_config['database']}")
        if 'username' in self.connection_config:
            parts.append(f"UID={self.connection_config['username']}")
        if 'password' in self.connection_config:
            parts.append(f"PWD={self.connection_config['password']}")

        # Use configured driver or default
        driver = self.connection_config.get('driver', 'SQL Server')
        parts.append(f"Driver={{{driver}}}")

        # Trust certificate
        trust_cert = self.connection_config.get('trust_certificate', 'yes')
        parts.append(f"TrustServerCertificate={trust_cert}")

        return ";".join(parts)

    def enrich_with_ai_descriptions(self, ai_agent) -> Dict[str, TableInfo]:
        """
        Use AI agent to enrich table and column descriptions

        Args:
            ai_agent: InstantNeo agent capable of analyzing database schemas

        Returns:
            Updated table information with AI-generated descriptions
        """
        enriched_tables = {}

        if self.tables is None or len(self.tables) == 0:
            print("No tables available for enrichment")
            return enriched_tables

        print(f"Starting enrichment for {len(self.tables)} tables...")

        for table_name, table_info in self.tables.items():
            print(f"\n🔄 Processing table: {table_name} ({len(table_info.columns)} columns)")

            if table_info.ai_enriched:
                print(f"  ⏭️ Skipping {table_name} - already enriched")
                enriched_tables[table_name] = table_info
                continue  # Skip already enriched tables

            # Prepare context for AI
            table_context = {
                "table_name": f"{table_info.schema}.{table_info.name}",
                "columns": [
                    {
                        "name": col.name,
                        "type": col.data_type,
                        "nullable": col.is_nullable,
                        "samples": col.sample_values[:3]
                    }
                    for col in table_info.columns
                ],
                "row_count": table_info.row_count_estimate
            }

            prompt = f"""
            Analiza esta tabla de base de datos y proporciona descripciones útiles:

            {json.dumps(table_context, indent=2)}

            Proporciona en formato JSON:
            1. table_description: Descripción clara de qué contiene la tabla
            2. column_descriptions: Para cada columna, una descripción de qué representa

            Considera que es una base de datos de SERFOR (organismo forestal de Perú).
            """

            try:
                response = ai_agent.run(prompt)
                print(f"  AI response for {table_name}: {response[:100]}...")

                # Clean JSON response (remove backticks and code blocks)
                cleaned_response = response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()

                # Try to parse JSON response
                try:
                    enrichment_data = json.loads(cleaned_response)

                    # Apply enrichments
                    if 'table_description' in enrichment_data:
                        table_info.description = enrichment_data['table_description']

                    if 'column_descriptions' in enrichment_data:
                        for col in table_info.columns:
                            if col.name in enrichment_data['column_descriptions']:
                                # Handle nested description format
                                col_desc = enrichment_data['column_descriptions'][col.name]
                                if isinstance(col_desc, dict) and 'description' in col_desc:
                                    col.description = col_desc['description']
                                elif isinstance(col_desc, str):
                                    col.description = col_desc
                                col.ai_enriched = True

                    table_info.ai_enriched = True
                    table_info.last_updated = datetime.now().isoformat()

                except json.JSONDecodeError as je:
                    print(f"  JSON parse error for {table_name}: {je}")
                    print(f"  Cleaned response: {cleaned_response[:200]}...")
                    # Set basic description fallback
                    table_info.description = f"Tabla de datos SERFOR: {table_name}"

            except Exception as e:
                print(f"  Error enriching table {table_name}: {e}")

            enriched_tables[table_name] = table_info

        # Save updated cache
        self._save_cache()
        return enriched_tables

    def get_table_info(self, table_name: str) -> Optional[TableInfo]:
        """Get information about a specific table"""
        return self.tables.get(table_name)

    def get_all_tables(self) -> List[TableInfo]:
        """Get information about all tables"""
        return list(self.tables.values())

    def get_schema_for_ai(self, table_names: List[str] = None) -> Dict[str, Any]:
        """Get schema information formatted for AI consumption"""
        tables_to_include = table_names or list(self.tables.keys())

        schema_info = {
            "database_overview": {
                "total_tables": len(self.tables),
                "last_discovery": max([t.last_updated for t in self.tables.values()]) if self.tables else None
            },
            "tables": {},
            "relationships": self._get_table_relationships()
        }

        for table_name in tables_to_include:
            table = self.get_table_info(table_name)
            if table:
                schema_info["tables"][table_name] = {
                    "full_name": f"{table.schema}.{table.name}",
                    "description": table.description,
                    "estimated_rows": table.row_count_estimate,
                    "columns": [
                        {
                            "name": col.name,
                            "type": col.data_type,
                            "nullable": col.is_nullable,
                            "description": col.description,
                            "sample_values": col.sample_values[:3]
                        }
                        for col in table.columns
                    ]
                }

        return schema_info

    def _get_table_relationships(self) -> Dict[str, Any]:
        """
        Define known table relationships for AI agents

        Returns:
            Dictionary mapping relationship descriptions to JOIN conditions
        """
        return {
            "infractor_to_titulo_habilitante_by_codigo": {
                "description": "Relacionar infractores con títulos habilitantes por código de título",
                "join_condition": "V_INFRACTOR.TituloHabilitante = V_TITULOHABILITANTE.TituloHabilitante",
                "tables": ["V_INFRACTOR", "V_TITULOHABILITANTE"],
                "relationship_type": "many_to_one",
                "confidence": 0.9
            },
            "infractor_to_titulo_habilitante_by_titular": {
                "description": "Relacionar infractores con títulos habilitantes por nombre del titular",
                "join_condition": "V_INFRACTOR.Titular = V_TITULOHABILITANTE.Titular",
                "tables": ["V_INFRACTOR", "V_TITULOHABILITANTE"],
                "relationship_type": "many_to_one",
                "confidence": 0.8
            },
            "infractor_to_titulo_habilitante_by_documento": {
                "description": "Relacionar infractores con títulos habilitantes por número de documento",
                "join_condition": "V_INFRACTOR.NumeroDocumento = V_TITULOHABILITANTE.NumeroDocumento",
                "tables": ["V_INFRACTOR", "V_TITULOHABILITANTE"],
                "relationship_type": "many_to_one",
                "confidence": 0.85
            }
        }

    def _load_cache(self):
        """Load cached schema information"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for table_name, table_data in data.items():
                    # Convert dict back to TableInfo
                    columns = [ColumnInfo(**col_data) for col_data in table_data.get('columns', [])]
                    table_data['columns'] = columns
                    self.tables[table_name] = TableInfo(**table_data)

            except Exception as e:
                print(f"Error loading schema cache: {e}")

    def _save_cache(self):
        """Save schema information to cache"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

            # Convert to serializable format
            cache_data = {}
            for table_name, table_info in self.tables.items():
                table_dict = asdict(table_info)
                cache_data[table_name] = table_dict

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error saving schema cache: {e}")

    def refresh_schema(self, connection_string: str = None) -> bool:
        """Force refresh of schema information"""
        try:
            self.discover_schema(connection_string)
            return True
        except Exception as e:
            print(f"Error refreshing schema: {e}")
            return False