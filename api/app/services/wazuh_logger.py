"""
WAZUH-compatible JSON logger for SERFOR API
Logs authentication events, queries, and SQL executions
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class WazuhLogger:
    """
    JSON logger compatible with WAZUH SIEM

    Log format:
    {
        "timestamp": "2025-12-09T12:00:00.000Z",
        "event_type": "login|query|error",
        "user_id": 123,
        "user_name": "admin",
        "source_ip": "192.168.1.1",
        "natural_query": "¿Cuántos infractores hay?",
        "sql_executed": "SELECT COUNT(*) FROM [MASKED]",
        "http_status": 200,
        "success": true,
        "details": {}
    }
    """

    # =====================================================
    # CONFIGURACIÓN DE RUTA DE LOGS
    # DEV:  "logs/wazuh" (relativo al directorio api/)
    # PROD: "/var/log/serforia"
    # =====================================================
    LOG_DIR = Path("logs/wazuh")
    LOG_FILE = "serfor_audit.log"

    # Patrones para enmascarar datos sensibles en SQL
    MASK_PATTERNS = [
        (r"'[^']*'", "'[MASKED]'"),  # Strings entre comillas simples
        (r'"[^"]*"', '"[MASKED]"'),  # Strings entre comillas dobles
        (r'\b\d{8}\b', '[DNI_MASKED]'),  # DNI (8 dígitos)
        (r'\b\d{11}\b', '[RUC_MASKED]'),  # RUC (11 dígitos)
    ]

    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize WAZUH logger

        Args:
            log_dir: Custom log directory path. If None, uses default.
        """
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = self.LOG_DIR

        self._ensure_log_dir()
        self.log_file = self.log_dir / self.LOG_FILE

    def _ensure_log_dir(self):
        """Create log directory if it doesn't exist"""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create log directory {self.log_dir}: {e}")

    def _mask_sql(self, sql: str) -> str:
        """
        Mask sensitive data in SQL queries

        Args:
            sql: Original SQL query

        Returns:
            Masked SQL query
        """
        if not sql:
            return ""

        masked = sql
        for pattern, replacement in self.MASK_PATTERNS:
            masked = re.sub(pattern, replacement, masked)
        return masked

    def _write_log(self, event: dict):
        """
        Write log event to JSON file

        Args:
            event: Log event dictionary
        """
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to write WAZUH log: {e}")

    def log_login(
        self,
        user_id: Optional[int],
        user_name: str,
        source_ip: str,
        success: bool,
        http_status: int = 200,
        error_message: Optional[str] = None,
        auth_mode: str = "SGI"
    ):
        """
        Log authentication attempt

        Args:
            user_id: User ID (None if login failed)
            user_name: Username attempted
            source_ip: Client IP address
            success: Whether login was successful
            http_status: HTTP response status code
            error_message: Error message if login failed
            auth_mode: Authentication mode (SGI or DEV)
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "login",
            "user_id": user_id,
            "user_name": user_name,
            "source_ip": source_ip,
            "natural_query": None,
            "sql_executed": None,
            "http_status": http_status,
            "success": success,
            "details": {
                "auth_mode": auth_mode,
                "error": error_message
            }
        }
        self._write_log(event)
        logger.info(f"WAZUH | login | user={user_name} | ip={source_ip} | success={success}")

    def log_query(
        self,
        user_id: int,
        user_name: str,
        source_ip: str,
        natural_query: str,
        sql_queries: Optional[List[str]] = None,
        http_status: int = 200,
        success: bool = True,
        error_message: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        rejected: bool = False,
        rejection_reason: Optional[str] = None
    ):
        """
        Log natural language query and SQL execution

        Args:
            user_id: Authenticated user ID
            user_name: Authenticated user name
            source_ip: Client IP address
            natural_query: User's natural language query
            sql_queries: List of SQL queries executed (will be masked)
            http_status: HTTP response status code
            success: Whether query was successful
            error_message: Error message if query failed
            response_time_ms: Response time in milliseconds
            rejected: Whether query was rejected by guardrails
            rejection_reason: Reason for rejection (if rejected)
        """
        # Mask SQL queries
        masked_sql = None
        if sql_queries:
            masked_sql = [self._mask_sql(sql) for sql in sql_queries]

        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "query",
            "user_id": user_id,
            "user_name": user_name,
            "source_ip": source_ip,
            "natural_query": natural_query,
            "sql_executed": masked_sql,
            "http_status": http_status,
            "success": success,
            "details": {
                "error": error_message,
                "response_time_ms": response_time_ms,
                "sql_count": len(sql_queries) if sql_queries else 0,
                "rejected": rejected,
                "rejection_reason": rejection_reason
            }
        }
        self._write_log(event)
        log_msg = f"WAZUH | query | user={user_name} | ip={source_ip} | success={success}"
        if rejected:
            log_msg += f" | rejected=true | reason={rejection_reason}"
        logger.info(log_msg)

    def log_error(
        self,
        user_id: Optional[int],
        user_name: Optional[str],
        source_ip: str,
        http_status: int,
        error_message: str,
        endpoint: str,
        natural_query: Optional[str] = None
    ):
        """
        Log application error

        Args:
            user_id: User ID if authenticated
            user_name: User name if authenticated
            source_ip: Client IP address
            http_status: HTTP response status code
            error_message: Error description
            endpoint: API endpoint that caused the error
            natural_query: Natural query if applicable
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "error",
            "user_id": user_id,
            "user_name": user_name,
            "source_ip": source_ip,
            "natural_query": natural_query,
            "sql_executed": None,
            "http_status": http_status,
            "success": False,
            "details": {
                "error": error_message,
                "endpoint": endpoint
            }
        }
        self._write_log(event)
        logger.warning(f"WAZUH | error | user={user_name} | ip={source_ip} | status={http_status}")


# Singleton instance
_wazuh_logger: Optional[WazuhLogger] = None


def get_wazuh_logger() -> WazuhLogger:
    """
    Get singleton instance of WazuhLogger

    Returns:
        WazuhLogger instance
    """
    global _wazuh_logger
    if _wazuh_logger is None:
        _wazuh_logger = WazuhLogger()
    return _wazuh_logger
