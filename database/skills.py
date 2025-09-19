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
        "query": "SQL SELECT query to execute",
        "max_rows": "Maximum number of rows to return (default: 100)"
    }
)
def execute_select_query(query: str, max_rows: int = 100) -> str:
    """
    Execute a SELECT query safely on the database

    Args:
        query: SQL SELECT query
        max_rows: Maximum rows to return

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
        result = db_manager.execute_query_safely(query, max_rows)

        # Log the executed query
        print(f"🔍 SQL EJECUTADO: {query}")
        logger.log_sql_query(query, result["success"], result.get("row_count", 0), result.get("error"))

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
    description="Get a sample of data from a specific table",
    parameters={
        "schema_name": "Database schema name (e.g., 'Dir')",
        "table_name": "Table name to sample",
        "limit": "Number of sample rows to return (default: 5)"
    }
)
def get_table_sample(schema_name: str, table_name: str, limit: int = 5) -> str:
    """
    Get sample data from a table

    Args:
        schema_name: Database schema name
        table_name: Table name
        limit: Number of rows to sample

    Returns:
        JSON string with sample data
    """
    try:
        result = db_manager.get_table_sample(schema_name, table_name, limit)

        if result["success"]:
            return json.dumps({
                "success": True,
                "sample_data": result["data"],
                "columns": result["columns"],
                "table": f"{schema_name}.{table_name}",
                "sample_size": len(result["data"])
            })
        else:
            return json.dumps({
                "success": False,
                "error": result["error"]
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error sampling table: {str(e)}"
        })

@skill(
    description="Count total rows in a table",
    parameters={
        "schema_name": "Database schema name (e.g., 'Dir')",
        "table_name": "Table name to count"
    }
)
def count_table_rows(schema_name: str, table_name: str) -> str:
    """
    Count total rows in a table

    Args:
        schema_name: Database schema name
        table_name: Table name

    Returns:
        JSON string with row count
    """
    try:
        result = db_manager.get_table_count(schema_name, table_name)

        if result["success"]:
            return json.dumps({
                "success": True,
                "table": f"{schema_name}.{table_name}",
                "row_count": result["count"]
            })
        else:
            return json.dumps({
                "success": False,
                "error": result["error"]
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error counting rows: {str(e)}"
        })

@skill(
    description="Search for data using flexible filters",
    parameters={
        "schema_name": "Database schema name",
        "table_name": "Table name to search",
        "filters": "JSON string with column filters (e.g., '{\"column_name\": \"value\", \"date_column\": \">2022-01-01\"}')",
        "limit": "Maximum number of results (default: 50)"
    }
)
def search_table_data(schema_name: str, table_name: str, filters: str, limit: int = 50) -> str:
    """
    Search table data with flexible filters

    Args:
        schema_name: Database schema name
        table_name: Table name
        filters: JSON string with filter conditions
        limit: Maximum results to return

    Returns:
        JSON string with search results
    """
    try:
        # Parse filters
        filter_dict = json.loads(filters) if filters else {}

        # Build WHERE clause
        where_conditions = []
        for column, condition in filter_dict.items():
            if isinstance(condition, str):
                if condition.startswith(('>', '<', '>=', '<=', '!=')):
                    # Handle comparison operators
                    where_conditions.append(f"[{column}] {condition}")
                else:
                    # Handle string matching
                    if '%' in condition:
                        where_conditions.append(f"[{column}] LIKE '{condition}'")
                    else:
                        where_conditions.append(f"[{column}] = '{condition}'")
            else:
                where_conditions.append(f"[{column}] = {condition}")

        # Build query
        base_query = f"SELECT TOP {limit} * FROM [{schema_name}].[{table_name}]"
        if where_conditions:
            query = f"{base_query} WHERE {' AND '.join(where_conditions)}"
        else:
            query = base_query

        # Execute query
        result = db_manager.execute_query(query)

        if result["success"]:
            return json.dumps({
                "success": True,
                "data": result["data"],
                "columns": result["columns"],
                "row_count": result["row_count"],
                "query_used": query,
                "filters_applied": filter_dict
            })
        else:
            return json.dumps({
                "success": False,
                "error": result["error"],
                "query_attempted": query
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error searching data: {str(e)}"
        })

@skill(
    description="Aggregate data using common functions (COUNT, SUM, AVG, etc.)",
    parameters={
        "schema_name": "Database schema name",
        "table_name": "Table name",
        "aggregate_function": "Function to use (COUNT, SUM, AVG, MIN, MAX)",
        "column_name": "Column to aggregate (use * for COUNT)",
        "group_by": "Column to group by (optional)",
        "filters": "JSON string with filter conditions (optional)"
    }
)
def aggregate_table_data(
    schema_name: str,
    table_name: str,
    aggregate_function: str,
    column_name: str,
    group_by: Optional[str] = None,
    filters: Optional[str] = None
) -> str:
    """
    Perform aggregation operations on table data

    Args:
        schema_name: Database schema name
        table_name: Table name
        aggregate_function: Aggregation function
        column_name: Column to aggregate
        group_by: Optional grouping column
        filters: Optional filter conditions

    Returns:
        JSON string with aggregation results
    """
    try:
        # Validate aggregate function
        valid_functions = ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX']
        if aggregate_function.upper() not in valid_functions:
            return json.dumps({
                "success": False,
                "error": f"Invalid aggregate function. Use one of: {valid_functions}"
            })

        # Build SELECT clause
        if column_name == '*' and aggregate_function.upper() == 'COUNT':
            select_clause = "COUNT(*) as count_result"
        else:
            select_clause = f"{aggregate_function.upper()}([{column_name}]) as {aggregate_function.lower()}_result"

        if group_by:
            select_clause = f"[{group_by}], {select_clause}"

        # Build WHERE clause from filters
        where_clause = ""
        if filters:
            filter_dict = json.loads(filters)
            where_conditions = []
            for col, condition in filter_dict.items():
                if isinstance(condition, str) and not condition.startswith(('>', '<', '>=', '<=', '!=')):
                    where_conditions.append(f"[{col}] = '{condition}'")
                else:
                    where_conditions.append(f"[{col}] {condition}")

            if where_conditions:
                where_clause = f"WHERE {' AND '.join(where_conditions)}"

        # Build complete query
        query = f"SELECT {select_clause} FROM [{schema_name}].[{table_name}]"
        if where_clause:
            query += f" {where_clause}"
        if group_by:
            query += f" GROUP BY [{group_by}]"

        # Execute query
        result = db_manager.execute_query(query)

        if result["success"]:
            return json.dumps({
                "success": True,
                "data": result["data"],
                "columns": result["columns"],
                "row_count": result["row_count"],
                "aggregation": {
                    "function": aggregate_function,
                    "column": column_name,
                    "group_by": group_by
                },
                "query_used": query
            })
        else:
            return json.dumps({
                "success": False,
                "error": result["error"],
                "query_attempted": query
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error performing aggregation: {str(e)}"
        })

@skill(
    description="Execute complex SQL queries with JOINs between tables",
    parameters={
        "query": "Complete SQL query with JOINs, WHERE clauses, etc.",
        "max_rows": "Maximum number of rows to return (default: 100)"
    }
)
def execute_complex_query(query: str, max_rows: int = 100) -> str:
    """
    Execute complex SQL queries that involve JOINs, subqueries, etc.

    Args:
        query: Complete SQL query string
        max_rows: Maximum rows to return

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
        result = db_manager.execute_query_safely(query, max_rows)

        # Log the executed query
        print(f"🔍 COMPLEX SQL EJECUTADO: {query}")
        logger.log_sql_query(query, result["success"], result.get("row_count", 0), result.get("error"))

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