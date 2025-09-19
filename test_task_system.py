"""
Test script for the new task management system
"""
from agents.task_manager import TaskManager, ExecutionTask, TaskStatus
from agents.planner_agent import PlannerAgent
import json

def test_task_manager():
    """Test basic task manager functionality"""
    print("🧪 Testing Task Manager...")

    # Create task manager
    tm = TaskManager()

    # Create test tasks
    task1 = ExecutionTask(
        description="Validate user input",
        action_type="validate",
        parameters={"input": "test query"},
        dependencies=[]
    )

    task2 = ExecutionTask(
        description="Query database",
        action_type="query",
        parameters={"table": "T_GEP_INFRACTORES"},
        dependencies=[]  # Will be updated after adding task1
    )

    task3 = ExecutionTask(
        description="Format results",
        action_type="format",
        parameters={"format": "table"},
        dependencies=[]  # Will be updated after adding task2
    )

    # Add tasks
    task1_id = tm.add_task(task1)
    task2_id = tm.add_task(task2)
    task3_id = tm.add_task(task3)

    # Update dependencies
    task2.dependencies = [task1_id]
    task3.dependencies = [task2_id]

    print(f"✅ Created {len(tm.tasks)} tasks")

    # Test execution order
    print("\n🔄 Testing execution order...")
    execution_order = []

    while not tm.is_execution_complete():
        next_task = tm.get_next_executable_task()
        if next_task:
            print(f"   Next: {next_task.description}")
            execution_order.append(next_task.description)
            next_task.complete_success(f"Mock result for {next_task.description}")
        else:
            break

    print(f"✅ Execution order: {execution_order}")

    # Test summary
    summary = tm.get_execution_summary()
    print(f"\n📊 Final summary: {summary['status_counts']}")

    return tm

def test_planner_integration():
    """Test planner integration with task manager"""
    print("\n🧪 Testing Planner Integration...")

    # Create mock plan JSON
    mock_plan = {
        "steps": [
            {
                "step_id": 1,
                "description": "Validate query parameters",
                "action_type": "validate",
                "parameters": {"query": "test"},
                "dependencies": [],
                "max_retries": 2
            },
            {
                "step_id": 2,
                "description": "Execute database query",
                "action_type": "query",
                "parameters": {"sql": "SELECT * FROM T_GEP_INFRACTORES"},
                "dependencies": [1],
                "max_retries": 3
            }
        ]
    }

    # Test planner task creation
    planner = PlannerAgent()
    task_manager = planner.create_task_manager_from_plan(json.dumps(mock_plan))

    print(f"✅ Created task manager with {len(task_manager.tasks)} tasks")

    # Show task details
    for task in task_manager.tasks:
        print(f"   - {task.description} (deps: {task.dependencies})")

    return task_manager

def main():
    """Run all tests"""
    print("🚀 Testing New Task Management System\n")

    # Test 1: Basic task manager
    tm1 = test_task_manager()

    # Test 2: Planner integration
    tm2 = test_planner_integration()

    print("\n✅ All tests completed!")
    print("\nTask Manager States:")
    print("Basic TM:", tm1.to_dict()["execution_summary"])
    print("Planner TM:", tm2.to_dict()["execution_summary"])

if __name__ == "__main__":
    main()