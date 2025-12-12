"""
Comprehensive logging system for SERFOR multi-agent system
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import time

class SerforLogger:
    """Centralized logging system for the SERFOR multi-agent system"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create session-specific log file (only detailed txt)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.detailed_log_file = self.log_dir / f"detailed_{self.session_id}.txt"

        # Track timing for performance metrics
        self.query_start_time: float = None
        self.agent_start_times: Dict[str, float] = {}
        self.current_task_id: str = None

        self._write_detailed_log(f"=== SESSION STARTED: {self.session_id} ===")

    def log_user_query(self, query: str):
        """Log user query and start query timer"""
        self.query_start_time = time.time()
        self._write_detailed_log(f"\n{'='*80}")
        self._write_detailed_log(f"USER QUERY: {query}")
        self._write_detailed_log(f"{'='*80}")

    def log_agent_activity(self, agent_name: str, action: str, input_data: Any = None, output_data: Any = None, error: str = None):
        """Log agent activity (simplified, no redundant data)"""
        status = "SUCCESS" if error is None else "ERROR"
        self._write_detailed_log(f"AGENT [{agent_name}] {action}: {status}")
        if error:
            self._write_detailed_log(f"  ERROR: {error}")

    def log_sql_query(self, query: str, success: bool, result_count: int = 0, error: str = None, columns: List[str] = None):
        """Log SQL query execution with summary (no raw data)"""
        task_context = f" (task: {self.current_task_id})" if self.current_task_id else ""
        status = "SUCCESS" if success else "ERROR"
        self._write_detailed_log(f"SQL QUERY {status}{task_context}:")
        self._write_detailed_log(f"  QUERY: {query}")
        if success:
            col_info = f", columns: {columns}" if columns else ""
            self._write_detailed_log(f"  RESULT: {result_count} rows{col_info}")
        else:
            self._write_detailed_log(f"  ERROR: {error}")

    def log_error(self, component: str, error_message: str, context: Dict[str, Any] = None):
        """Log errors"""
        self._write_detailed_log(f"ERROR in {component}: {error_message}")
        if context:
            self._write_detailed_log(f"  CONTEXT: {self._safe_str(context)}")

    def log_task_execution(self, task_id: str, description: str, status: str, result: Any = None, error: str = None):
        """Log task execution details"""
        # Track current task for SQL query context
        if status == "in_progress":
            self.current_task_id = task_id
        elif status in ("success", "failed", "completed"):
            self.current_task_id = None

        self._write_detailed_log(f"TASK [{task_id[:8]}] {description}: {status}")
        if error:
            self._write_detailed_log(f"  ERROR: {error}")

    def log_json_parsing(self, agent_name: str, raw_response: str, parsed_data: Any = None, error: str = None):
        """Log JSON parsing attempts (only log errors, success is implicit)"""
        if error:
            self._write_detailed_log(f"JSON PARSING ERROR in {agent_name}:")
            self._write_detailed_log(f"  RAW RESPONSE: {raw_response}")
            self._write_detailed_log(f"  ERROR: {error}")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            "session_id": self.session_id,
            "detailed_log": str(self.detailed_log_file)
        }

    # =========================================================================
    # NEW METHODS: Agent execution logging with prompts
    # =========================================================================

    def log_agent_start(self, agent_name: str, system_prompt: str, run_prompt: str):
        """Log agent execution start with full prompts"""
        self.agent_start_times[agent_name] = time.time()
        self._write_detailed_log(f"\n--- AGENT [{agent_name}] START ---")
        self._write_detailed_log(f"SYSTEM PROMPT:\n{system_prompt}")
        self._write_detailed_log(f"\nRUN PROMPT:\n{run_prompt}")

    def log_agent_end(self, agent_name: str, response: str, error: str = None):
        """Log agent execution end with full response and timing"""
        duration = None
        if agent_name in self.agent_start_times:
            duration = time.time() - self.agent_start_times[agent_name]
            del self.agent_start_times[agent_name]

        duration_str = f" ({duration:.2f}s)" if duration else ""
        status = "SUCCESS" if error is None else "ERROR"

        self._write_detailed_log(f"\nRESPONSE:\n{response}")
        self._write_detailed_log(f"--- AGENT [{agent_name}] END: {status}{duration_str} ---")
        if error:
            self._write_detailed_log(f"  ERROR: {error}")

    def log_query_complete(self, success: bool, error: str = None):
        """Log query completion with total time"""
        duration = None
        if self.query_start_time:
            duration = time.time() - self.query_start_time
            self.query_start_time = None

        duration_str = f" in {duration:.2f}s" if duration else ""
        status = "SUCCESS" if success else "FAILED"

        self._write_detailed_log(f"\n{'='*80}")
        self._write_detailed_log(f"=== QUERY {status}{duration_str} ===")
        if error:
            self._write_detailed_log(f"ERROR: {error}")
        self._write_detailed_log(f"{'='*80}\n")

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