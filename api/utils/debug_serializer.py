"""
Debug serialization utilities for complex objects
"""
import json
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict
from agents.task_manager import TaskManager, ExecutionTask

class DebugEncoder(json.JSONEncoder):
    """Custom JSON encoder for debugging complex objects"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, TaskManager):
            return self._serialize_task_manager(obj)
        elif isinstance(obj, ExecutionTask):
            return self._serialize_execution_task(obj)
        elif hasattr(obj, '__dict__'):
            # For any other objects with attributes, serialize their dict
            return self._serialize_object_dict(obj)
        else:
            # Fallback for unserializable objects
            return f"<{type(obj).__name__}: {str(obj)[:100]}>"

    def _serialize_task_manager(self, task_manager: TaskManager) -> Dict[str, Any]:
        """Serialize TaskManager object"""
        try:
            return {
                "_type": "TaskManager",
                "tasks": [self._serialize_execution_task(task) for task in task_manager.tasks],
                "execution_summary": task_manager.get_execution_summary(),
                "task_count": len(task_manager.tasks),
                "status_counts": task_manager.get_execution_summary().get("status_counts", {})
            }
        except Exception as e:
            return {
                "_type": "TaskManager",
                "_error": f"Serialization failed: {str(e)}",
                "task_count": len(task_manager.tasks) if hasattr(task_manager, 'tasks') else 0
            }

    def _serialize_execution_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """Serialize ExecutionTask object"""
        try:
            return {
                "_type": "ExecutionTask",
                "id": task.id,
                "description": task.description,
                "action_type": task.action_type,
                "parameters": task.parameters,
                "dependencies": task.dependencies,
                "status": task.status.value if hasattr(task.status, 'value') else str(task.status),
                "retry_count": task.retry_count,
                "max_retries": task.max_retries,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "result": str(task.result)[:500] if task.result else None,  # Truncate long results
                "error_message": task.error_message
            }
        except Exception as e:
            return {
                "_type": "ExecutionTask",
                "_error": f"Serialization failed: {str(e)}",
                "id": getattr(task, 'id', 'unknown'),
                "description": getattr(task, 'description', 'unknown')
            }

    def _serialize_object_dict(self, obj: Any) -> Dict[str, Any]:
        """Serialize object's __dict__ with error handling"""
        try:
            result = {"_type": type(obj).__name__}
            for key, value in obj.__dict__.items():
                try:
                    # Try to serialize each attribute
                    if isinstance(value, (str, int, float, bool, type(None))):
                        result[key] = value
                    elif isinstance(value, (list, tuple)):
                        result[key] = [self.default(item) for item in value[:10]]  # Limit list size
                    elif isinstance(value, dict):
                        result[key] = {k: self.default(v) for k, v in list(value.items())[:10]}  # Limit dict size
                    else:
                        result[key] = self.default(value)
                except Exception as e:
                    result[key] = f"<serialization_error: {str(e)}>"
            return result
        except Exception as e:
            return {"_type": type(obj).__name__, "_error": f"Dict serialization failed: {str(e)}"}

def safe_json_dump(obj: Any, filepath: str = None, indent: int = 2) -> str:
    """
    Safely serialize any object to JSON string or file

    Args:
        obj: Object to serialize
        filepath: Optional file path to save JSON
        indent: JSON indentation level

    Returns:
        JSON string representation
    """
    try:
        json_str = json.dumps(obj, cls=DebugEncoder, indent=indent, ensure_ascii=False)

        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"✅ Debug data saved to: {filepath}")

        return json_str

    except Exception as e:
        error_data = {
            "_serialization_error": str(e),
            "_object_type": type(obj).__name__,
            "_object_str": str(obj)[:200]
        }
        json_str = json.dumps(error_data, indent=indent)

        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"⚠️ Error data saved to: {filepath}")

        return json_str

def debug_workflow_data(workflow_data: Dict[str, Any], query: str = "") -> str:
    """
    Create a debug dump of workflow_data with additional context

    Args:
        workflow_data: The workflow data to debug
        query: The original user query for context

    Returns:
        File path where debug data was saved
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_filename = f"debug/workflow_debug_{timestamp}.json"

    # Ensure debug directory exists
    import os
    os.makedirs("debug", exist_ok=True)

    # Create enhanced debug data
    debug_data = {
        "timestamp": datetime.now().isoformat(),
        "user_query": query,
        "workflow_data": workflow_data,
        "metadata": {
            "total_keys": len(workflow_data.keys()) if isinstance(workflow_data, dict) else 0,
            "keys": list(workflow_data.keys()) if isinstance(workflow_data, dict) else [],
            "workflow_data_type": type(workflow_data).__name__
        }
    }

    safe_json_dump(debug_data, debug_filename)
    return debug_filename