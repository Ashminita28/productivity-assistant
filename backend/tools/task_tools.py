from backend.services.task_service import TaskService

def execute_add_task(description: str) -> str:
    service = TaskService()
    task = service.add_task(description)
    return f"Task added successfully. (ID: {task.id})"

def execute_list_tasks() -> str:
    service = TaskService()
    tasks = service.get_all_tasks()
    if not tasks:
        return "You currently have no tasks."
    return "\n".join([f"{t.id}. {t.description} - {t.status}" for t in tasks])

def execute_update_task(task_id: int, status: str = None, description: str = None) -> str:
    service = TaskService()
    task = service.update_task(task_id, status, description)
    if task:
        return f"Task {task_id} updated. Status: {task.status}, Description: {task.description}"
    return f"Error: Task with ID {task_id} not found."

def execute_delete_task(task_id: int) -> str:
    service = TaskService()
    success = service.delete_task(task_id)
    if success:
        return f"Task {task_id} deleted successfully."
    return f"Error: Task with ID {task_id} not found."

def execute_summarize_tasks() -> str:
    service = TaskService()
    summary = service.get_summary()
    if summary["total"] == 0:
        return "You have no tasks to summarize."
        
    return (
        f"Total Tasks: {summary['total']}\n"
        f"Completed: {summary['completed']}\n"
        f"Pending: {summary['pending']}"
    )
