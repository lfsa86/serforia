"""
Comprehensive logging system for SERFOR multi-agent system
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

class SerforLogger:
    """Centralized logging system for the SERFOR multi-agent system"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create session-specific log file
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log_file = self.log_dir / f"session_{self.session_id}.json"
        self.detailed_log_file = self.log_dir / f"detailed_{self.session_id}.txt"

        # Initialize session log
        self.session_data = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "queries": [],
            "agents_activity": [],
            "sql_queries": [],
            "errors": [],
            "performance_metrics": {}
        }

        self._write_session_log()
        self._write_detailed_log(f"=== SESSION STARTED: {self.session_id} ===")

    def log_user_query(self, query: str):
        """Log user query"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "user_query",
            "query": query
        }
        self.session_data["queries"].append(entry)
        self._write_session_log()
        self._write_detailed_log(f"USER QUERY: {query}")

    def log_agent_activity(self, agent_name: str, action: str, input_data: Any = None, output_data: Any = None, error: str = None):
        """Log agent activity"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "input_summary": str(input_data) + "..." if input_data and len(str(input_data)) > 200 else str(input_data),
            "output_summary": str(output_data) + "..." if output_data and len(str(output_data)) > 200 else str(output_data),
            "error": error,
            "success": error is None
        }

        self.session_data["agents_activity"].append(entry)
        self._write_session_log()

        status = "SUCCESS" if error is None else "ERROR"
        self._write_detailed_log(f"AGENT [{agent_name}] {action}: {status}")
        if error:
            self._write_detailed_log(f"  ERROR: {error}")
        if input_data:
            self._write_detailed_log(f"  INPUT: {self._safe_str(input_data)}")
        if output_data:
            self._write_detailed_log(f"  OUTPUT: {self._safe_str(output_data)}")

    def log_sql_query(self, query: str, success: bool, result_count: int = 0, error: str = None):
        """Log SQL query execution"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "success": success,
            "result_count": result_count,
            "error": error
        }

        self.session_data["sql_queries"].append(entry)
        self._write_session_log()

        status = "SUCCESS" if success else "ERROR"
        self._write_detailed_log(f"SQL QUERY {status}: {query}")
        if success:
            self._write_detailed_log(f"  RESULTS: {result_count} rows")
        else:
            self._write_detailed_log(f"  ERROR: {error}")

    def log_error(self, component: str, error_message: str, context: Dict[str, Any] = None):
        """Log errors"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "error": error_message,
            "context": context
        }

        self.session_data["errors"].append(entry)
        self._write_session_log()
        self._write_detailed_log(f"ERROR in {component}: {error_message}")
        if context:
            self._write_detailed_log(f"  CONTEXT: {self._safe_str(context)}")

    def log_task_execution(self, task_id: str, description: str, status: str, result: Any = None, error: str = None):
        """Log task execution details"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "task_execution",
            "task_id": task_id,
            "description": description,
            "status": status,
            "result_summary": str(result) + "..." if result and len(str(result)) > 200 else str(result),
            "error": error
        }

        self.session_data["agents_activity"].append(entry)
        self._write_session_log()

        self._write_detailed_log(f"TASK [{task_id}] {description}: {status}")
        if result:
            self._write_detailed_log(f"  RESULT: {self._safe_str(result)}")
        if error:
            self._write_detailed_log(f"  ERROR: {error}")

    def log_json_parsing(self, agent_name: str, raw_response: str, parsed_data: Any = None, error: str = None):
        """Log JSON parsing attempts"""
        self._write_detailed_log(f"JSON PARSING in {agent_name}:")
        self._write_detailed_log(f"  RAW RESPONSE: {raw_response}")

        if error:
            self._write_detailed_log(f"  PARSING ERROR: {error}")
            self.log_error(f"{agent_name}_json_parsing", error, {"raw_response": raw_response})
        else:
            self._write_detailed_log(f"  PARSED DATA: {self._safe_str(parsed_data)}")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            "session_id": self.session_id,
            "queries_count": len(self.session_data["queries"]),
            "sql_queries_count": len(self.session_data["sql_queries"]),
            "errors_count": len(self.session_data["errors"]),
            "agents_activity_count": len(self.session_data["agents_activity"]),
            "log_files": {
                "session_log": str(self.session_log_file),
                "detailed_log": str(self.detailed_log_file)
            }
        }

    def _write_session_log(self):
        """Write session data to JSON file"""
        try:
            with open(self.session_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing session log: {e}")

    def _write_detailed_log(self, message: str):
        """Write detailed log entry"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            with open(self.detailed_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"Error writing detailed log: {e}")

    def _safe_str(self, obj: Any, max_length: int = 500) -> str:
        """Safely convert object to string with length limit"""
        try:
            str_repr = str(obj)
            if len(str_repr) > max_length:
                return str_repr[:max_length] + "..."
            return str_repr
        except Exception:
            return f"<Unable to convert {type(obj)} to string>"

# Global logger instance
_global_logger = None

def get_logger() -> SerforLogger:
    """Get global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = SerforLogger()
    return _global_logger

def init_logger(log_dir: str = "logs") -> SerforLogger:
    """Initialize global logger"""
    global _global_logger
    _global_logger = SerforLogger(log_dir)
    return _global_logger