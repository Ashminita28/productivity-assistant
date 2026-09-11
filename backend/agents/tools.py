from backend.repositories.task_repo import TaskRepository
from backend.config.database_config import SessionLocal

def execute_add_task(description: str) -> str:
    db = SessionLocal()
    try:
        repo = TaskRepository(db)
        task = repo.add_task(description)
        return f"Task added successfully. (ID: {task.id})"
    finally:
        db.close()

def execute_list_tasks() -> str:
    db = SessionLocal()
    try:
        repo = TaskRepository(db)
        tasks = repo.get_all_tasks()
        if not tasks:
            return "You currently have no tasks."
        return "\n".join([f"{t.id}. {t.description} - {t.status}" for t in tasks])
    finally:
        db.close()

def execute_update_task(task_id: int, status: str = "Completed") -> str:
    db = SessionLocal()
    try:
        repo = TaskRepository(db)
        task = repo.update_task_status(task_id, status)
        if task:
            return f"Task {task_id} updated to {status}."
        return f"Error: Task with ID {task_id} not found."
    finally:
        db.close()

def execute_delete_task(task_id: int) -> str:
    db = SessionLocal()
    try:
        repo = TaskRepository(db)
        success = repo.delete_task(task_id)
        if success:
            return f"Task {task_id} deleted successfully."
        return f"Error: Task with ID {task_id} not found."
    finally:
        db.close()

def execute_summarize_tasks() -> str:
    db = SessionLocal()
    try:
        repo = TaskRepository(db)
        summary = repo.get_summary()
        
        if summary["total"] == 0:
            return "You have no tasks to summarize."
            
        return (
            f"Total Tasks: {summary['total']}\n"
            f"Completed: {summary['completed']}\n"
            f"Pending: {summary['pending']}"
        )
    finally:
        db.close()
