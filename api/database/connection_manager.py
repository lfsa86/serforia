"""
Database Connection Manager - Handles SQL Server connections
"""
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime, date
import json

load_dotenv()

class DatabaseConnectionManager:
    """Manages database connections and basic operations"""

    def __init__(self):
        self.connection_config = self._load_default_config()
        self.connection = None

    def _serialize_value(self, value):
        """Convert non-JSON serializable types to serializable ones"""
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif value is None:
            return None
        else:
            return value

    def _load_default_config(self) -> Dict[str, str]:
        """Load default connection configuration"""
        return {
            "server": os.getenv("DB_SERVER", "localhost"),
            "port": os.getenv("DB_PORT", "1433"),
            "database": os.getenv("DB_DATABASE", "SERFOR_BDDWH"),
            "username": os.getenv("DB_USERNAME", "sa"),
            "password": os.getenv("DB_PASSWORD", "SerforDB@2025"),
            "driver": os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
            "trust_certificate": os.getenv("DB_TRUST_CERT", "yes")
        }

    def set_config(self, config: Dict[str, str]):
        """Set custom connection configuration"""
        self.connection_config.update(config)

    def get_connection_string(self) -> str:
        """Build connection string from configuration"""
        parts = [
            f"Driver={{{self.connection_config['driver']}}}",
            f"Server={self.connection_config['server']},{self.connection_config['port']}",
            f"Database={self.connection_config['database']}",
            f"UID={self.connection_config['username']}",
            f"PWD={self.connection_config['password']}",
            f"TrustServerCertificate={self.connection_config['trust_certificate']}"
        ]
        return ";".join(parts)

    def test_connection(self) -> Dict[str, Any]:
        """Test database connection"""
        try:
            import pyodbc
        except ImportError:
            return {
                "success": False,
                "error": "pyodbc not installed. Run: pip install pyodbc"
            }

        try:
            conn_str = self.get_connection_string()
            with pyodbc.connect(conn_str, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()

                return {
                    "success": True,
                    "message": "Connection successful",
                    "test_result": result[0] if result else None
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def execute_query(self, query: str, parameters: Optional[List] = None) -> Dict[str, Any]:
        """
        Execute a SQL query safely

        Args:
            query: SQL query string
            parameters: Optional parameters for parameterized queries

        Returns:
            Dictionary with results or error information
        """
        try:
            import pyodbc
        except ImportError:
            return {
                "success": False,
                "error": "pyodbc not installed"
            }

        try:
            conn_str = self.get_connection_string()
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()

                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)

                # Handle different query types
                if query.strip().upper().startswith('SELECT'):
                    # Fetch results for SELECT queries
                    columns = [column[0] for column in cursor.description] if cursor.description else []
                    rows = cursor.fetchall()

                    # Convert to list of dictionaries with proper serialization
                    results = []
                    for row in rows:
                        row_dict = {}
                        for i, value in enumerate(row):
                            row_dict[columns[i]] = self._serialize_value(value)
                        results.append(row_dict)

                    return {
                        "success": True,
                        "data": results,
                        "columns": columns,
                        "row_count": len(results)
                    }
                else:
                    # For non-SELECT queries
                    conn.commit()
                    return {
                        "success": True,
                        "message": "Query executed successfully",
                        "rows_affected": cursor.rowcount
                    }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def execute_query_safely(self, query: str, max_rows: int = 1000) -> Dict[str, Any]:
        """
        Execute query with safety limits and SQL Server syntax conversion

        Args:
            query: SQL query
            max_rows: Maximum number of rows to return

        Returns:
            Query results with safety checks
        """
        # Convert MySQL/PostgreSQL syntax to SQL Server
        query = self._convert_to_sqlserver_syntax(query, max_rows)

        return self.execute_query(query)

    def _convert_to_sqlserver_syntax(self, query: str, max_rows: int = 1000) -> str:
        """
        Convert MySQL/PostgreSQL syntax to SQL Server syntax

        Args:
            query: Original SQL query
            max_rows: Maximum rows for TOP clause

        Returns:
            Query converted to SQL Server syntax
        """
        import re

        # Convert LIMIT to TOP
        if 'LIMIT' in query.upper():
            # Pattern: LIMIT N or LIMIT N OFFSET M
            limit_pattern = r'\s+LIMIT\s+(\d+)(?:\s+OFFSET\s+(\d+))?'
            match = re.search(limit_pattern, query, re.IGNORECASE)

            if match:
                limit_num = match.group(1)
                offset_num = match.group(2)

                if offset_num:
                    # LIMIT N OFFSET M -> OFFSET M ROWS FETCH NEXT N ROWS ONLY
                    # Remove LIMIT clause
                    query = re.sub(limit_pattern, '', query, flags=re.IGNORECASE)
                    # Add ORDER BY if not present (required for OFFSET)
                    if 'ORDER BY' not in query.upper():
                        query = query.rstrip(';') + ' ORDER BY (SELECT NULL)'
                    query += f' OFFSET {offset_num} ROWS FETCH NEXT {limit_num} ROWS ONLY'
                else:
                    # LIMIT N -> TOP N
                    # Remove LIMIT clause
                    query = re.sub(limit_pattern, '', query, flags=re.IGNORECASE)
                    # Add TOP clause (handle DISTINCT)
                    query = self._add_top_clause(query, limit_num)

        # Add TOP if no limit specified and it's a SELECT
        elif query.strip().upper().startswith('SELECT') and 'TOP' not in query.upper() and 'OFFSET' not in query.upper():
            query = self._add_top_clause(query, max_rows)

        return query

    def _add_top_clause(self, query: str, limit: int) -> str:
        """
        Add TOP clause to SELECT query, handling DISTINCT correctly.

        SQL Server requires: SELECT DISTINCT TOP N ... (not SELECT TOP N DISTINCT)

        Args:
            query: SQL query
            limit: Number for TOP clause

        Returns:
            Query with TOP clause added correctly
        """
        import re

        # Pattern to match SELECT with optional DISTINCT/ALL
        # Handles: SELECT, SELECT DISTINCT, SELECT ALL
        pattern = r'^(\s*SELECT\s+)(DISTINCT\s+|ALL\s+)?'

        def replace_select(match):
            select_part = match.group(1)  # "SELECT "
            modifier = match.group(2) or ""  # "DISTINCT " or "ALL " or ""
            return f"{select_part}{modifier}TOP {limit} "

        return re.sub(pattern, replace_select, query, count=1, flags=re.IGNORECASE)

    def get_table_sample(self, schema: str, table: str, limit: int = 10) -> Dict[str, Any]:
        """Get a sample of data from a table"""
        query = f"SELECT TOP {limit} * FROM [{schema}].[{table}]"
        return self.execute_query(query)

    def get_table_count(self, schema: str, table: str) -> Dict[str, Any]:
        """Get row count for a table"""
        query = f"SELECT COUNT(*) as row_count FROM [{schema}].[{table}]"
        result = self.execute_query(query)

        if result["success"] and result["data"]:
            return {
                "success": True,
                "count": result["data"][0]["row_count"]
            }
        else:
            return result

    def validate_query_syntax(self, query: str) -> Dict[str, Any]:
        """
        Validate query syntax without executing

        Args:
            query: SQL query to validate

        Returns:
            Validation result
        """
        try:
            # Basic syntax validation
            query = query.strip()

            # Check for dangerous operations
            dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'UPDATE', 'INSERT']
            query_upper = query.upper()

            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    return {
                        "valid": False,
                        "error": f"Query contains potentially dangerous operation: {keyword}"
                    }

            # Check if it's a SELECT query
            if not query_upper.startswith('SELECT'):
                return {
                    "valid": False,
                    "error": "Only SELECT queries are allowed"
                }

            return {
                "valid": True,
                "message": "Query syntax appears valid"
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }

    def get_connection_info(self) -> Dict[str, Any]:
        """Get sanitized connection information"""
        info = self.connection_config.copy()
        # Remove sensitive information
        if 'password' in info:
            info['password'] = '***'
        return info