"""
Flexible Database Skills for InstantNeo agents
"""
from instantneo.skills import skill
from typing import Dict, Any, List, Optional
from .connection_manager import DatabaseConnectionManager
from .schema_mapper import DynamicSchemaMapper
from utils.logger import get_logger
import json

# Global instances
db_manager = DatabaseConnectionManager()
schema_mapper = DynamicSchemaMapper()
logger = get_logger()

@skill(
    description="Execute a safe SQL SELECT query on the SERFOR database",
    parameters={
        "query": "SQL SELECT query to execute"
    }
)
def execute_select_query(query: str) -> str:
    """
    Execute a SELECT query safely on the database

    Args:
        query: SQL SELECT query
        
    Returns:
        JSON string with query results
    """
    try:
        # Validate query syntax
        validation = db_manager.validate_query_syntax(query)
        if not validation["valid"]:
            return json.dumps({
                "success": False,
                "error": f"Query validation failed: {validation['error']}"
            })

        # Execute query with safety limits
        result = db_manager.execute_query_safely(query)

        # Log the executed query
        print(f"🔍 SQL EJECUTADO: {query}")
        logger.log_sql_query(query, result["success"], result.get("row_count", 0), result.get("error"), result.get("columns"))

        if result["success"]:
            print(f"✅ Consulta exitosa: {result['row_count']} filas devueltas")
            return json.dumps({
                "success": True,
                "data": result["data"],
                "columns": result["columns"],
                "row_count": result["row_count"],
                "query_executed": query,
                "message": f"Query executed successfully. Returned {result['row_count']} rows."
            })
        else:
            print(f"❌ Error en consulta: {result['error']}")
            return json.dumps({
                "success": False,
                "error": result["error"],
                "query_attempted": query
            })

    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        })

@skill(
    description="Get schema information for tables in the database",
    parameters={
        "table_names": "List of table names to get schema for (optional, gets all if not specified)"
    }
)
def get_table_schemas(table_names: Optional[str] = None) -> str:
    """
    Get schema information for specified tables

    Args:
        table_names: Comma-separated list of table names, or None for all

    Returns:
        JSON string with schema information
    """
    try:
        if table_names:
            # Parse comma-separated table names
            table_list = [name.strip() for name in table_names.split(",")]
        else:
            table_list = None

        schema_info = schema_mapper.get_schema_for_ai(table_list)

        return json.dumps({
            "success": True,
            "schema_info": schema_info
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error getting schema: {str(e)}"
        })

@skill(
    description="Execute complex SQL queries with JOINs between tables",
    parameters={
        "query": "Complete SQL query with JOINs, WHERE clauses, etc."
    }
)
def execute_complex_query(query: str) -> str:
    """
    Execute complex SQL queries that involve JOINs, subqueries, etc.

    Args:
        query: Complete SQL query string

    Returns:
        JSON string with query results
    """
    try:
        # Enhanced validation for complex queries
        validation = db_manager.validate_query_syntax(query)
        if not validation["valid"]:
            return json.dumps({
                "success": False,
                "error": f"Query validation failed: {validation['error']}"
            })

        # Execute complex query
        result = db_manager.execute_query_safely(query)

        # Log the executed query
        print(f"🔍 COMPLEX SQL EJECUTADO: {query}")
        logger.log_sql_query(query, result["success"], result.get("row_count", 0), result.get("error"), result.get("columns"))

        if result["success"]:
            print(f"✅ Consulta compleja exitosa: {result['row_count']} filas devueltas")
            return json.dumps({
                "success": True,
                "data": result["data"],
                "columns": result["columns"],
                "row_count": result["row_count"],
                "query_executed": query,
                "query_type": "complex_join",
                "message": f"Complex query executed successfully. Returned {result['row_count']} rows."
            })
        else:
            print(f"❌ Error en consulta compleja: {result['error']}")
            return json.dumps({
                "success": False,
                "error": result["error"],
                "query_attempted": query,
                "query_type": "complex_join"
            })

    except Exception as e:
        print(f"❌ Error inesperado en consulta compleja: {str(e)}")
        logger.log_error("complex_query_execution", str(e), {"query": query})
        return json.dumps({
            "success": False,
            "error": f"Unexpected error in complex query: {str(e)}"
        })

@skill(
    description="Test database connection",
    parameters={}
)
def test_database_connection() -> str:
    """
    Test the database connection

    Returns:
        JSON string with connection test results
    """
    try:
        result = db_manager.test_connection()
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Connection test failed: {str(e)}"
        })

@skill(
    description="Discover and refresh database schema information",
    parameters={}
)
def refresh_database_schema() -> str:
    """
    Refresh the database schema information by discovering current structure

    Returns:
        JSON string with schema refresh results
    """
    try:
        # Set connection config for schema mapper
        schema_mapper.set_connection_config(db_manager.connection_config)

        # Discover schema
        discovered_tables = schema_mapper.discover_schema()

        return json.dumps({
            "success": True,
            "message": f"Schema refreshed successfully. Discovered {len(discovered_tables)} tables.",
            "tables_discovered": list(discovered_tables.keys())
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Schema refresh failed: {str(e)}"
        })