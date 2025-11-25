"""
Task Management System for execution planning and monitoring
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ExecutionTask:
    """Represents a single executable task"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    action_type: str = ""  # query, validate, transform, calculate, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

    def start_execution(self):
        """Mark task as in progress"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete_success(self, result: Any):
        """Mark task as completed with result"""
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()

    def complete_failure(self, error: str):
        """Mark task as failed with error"""
        self.status = TaskStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now()

    def can_execute(self, completed_tasks: List[str]) -> bool:
        """Check if task dependencies are satisfied"""
        return all(dep_id in completed_tasks for dep_id in self.dependencies)

    def should_retry(self) -> bool:
        """Check if task should be retried"""
        return self.status == TaskStatus.FAILED and self.retry_count < self.max_retries

class TaskManager:
    """Manages execution tasks with dependencies and error recovery"""

    def __init__(self):
        self.tasks: List[ExecutionTask] = []
        self.execution_log: List[Dict[str, Any]] = []

    def add_task(self, task: ExecutionTask) -> str:
        """Add a task to the manager"""
        self.tasks.append(task)
        self.log_event("task_added", {"task_id": task.id, "description": task.description})
        return task.id

    def create_task_from_plan_step(self, step: Dict[str, Any], dependencies: List[str] = None) -> ExecutionTask:
        """Create task from planner output step"""
        return ExecutionTask(
            description=step.get("description", ""),
            action_type=step.get("action_type", "unknown"),
            parameters=step.get("parameters", {}),
            dependencies=dependencies or [],
            max_retries=step.get("max_retries", 3)
        )

    def get_next_executable_task(self) -> Optional[ExecutionTask]:
        """Get the next task that can be executed"""
        completed_task_ids = [t.id for t in self.tasks if t.status == TaskStatus.COMPLETED]

        for task in self.tasks:
            if task.status == TaskStatus.PENDING and task.can_execute(completed_task_ids):
                return task

        # Check for failed tasks that can be retried
        for task in self.tasks:
            if task.should_retry():
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                self.log_event("task_retry", {"task_id": task.id, "retry_count": task.retry_count})
                return task

        return None

    def get_tasks_by_status(self, status: TaskStatus) -> List[ExecutionTask]:
        """Get all tasks with specific status"""
        return [task for task in self.tasks if task.status == status]

    def is_execution_complete(self) -> bool:
        """Check if all tasks are completed or definitively failed"""
        for task in self.tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                return False
            if task.status == TaskStatus.FAILED and task.should_retry():
                return False
        return True

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution status"""
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len(self.get_tasks_by_status(status))

        failed_tasks = self.get_tasks_by_status(TaskStatus.FAILED)
        failed_details = [{"id": t.id, "description": t.description, "error": t.error_message}
                         for t in failed_tasks if not t.should_retry()]

        return {
            "total_tasks": len(self.tasks),
            "status_counts": status_counts,
            "is_complete": self.is_execution_complete(),
            "failed_tasks": failed_details,
            "execution_log": self.execution_log[-10:]  # Last 10 events
        }

    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log execution event"""
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        })

    def create_recovery_plan(self) -> List[ExecutionTask]:
        """Create recovery tasks for failed operations"""
        recovery_tasks = []
        failed_tasks = [t for t in self.tasks if t.status == TaskStatus.FAILED and not t.should_retry()]

        for failed_task in failed_tasks:
            # Create alternative approach task
            recovery_task = ExecutionTask(
                description=f"Recovery for: {failed_task.description}",
                action_type="recovery_" + failed_task.action_type,
                parameters={**failed_task.parameters, "original_error": failed_task.error_message},
                dependencies=[],  # Recovery tasks usually don't depend on others
                max_retries=1
            )
            recovery_tasks.append(recovery_task)

        return recovery_tasks

    def to_dict(self) -> Dict[str, Any]:
        """Export task manager state to dictionary"""
        return {
            "tasks": [
                {
                    "id": task.id,
                    "description": task.description,
                    "action_type": task.action_type,
                    "parameters": task.parameters,
                    "dependencies": task.dependencies,
                    "status": task.status.value,
                    "result": str(task.result) if task.result else None,
                    "error_message": task.error_message,
                    "retry_count": task.retry_count
                }
                for task in self.tasks
            ],
            "execution_summary": self.get_execution_summary()
        }