from typing import Optional, Type
from pydantic import BaseModel
from langchain_core.tools import BaseTool
from backend.services.task_service import TaskService
from backend.schemas.agent_schemas import AddTaskInput, UpdateTaskInput, DeleteTaskInput

class AddTaskTool(BaseTool):
    name: str = "add_task"
    description: str = "Adds a new task to the user's to-do list."
    args_schema: Type[BaseModel] = AddTaskInput

    def _run(self, description: str) -> str:
        service = TaskService()
        task = service.add_task(description)
        return f"Task added successfully. (ID: {task.id})"

class ListTasksTool(BaseTool):
    name: str = "list_tasks"
    description: str = "Retrieves and lists all tasks on the user's to-do list. Use this when the user asks to see their tasks."

    def _run(self) -> str:
        service = TaskService()
        tasks = service.get_all_tasks()
        if not tasks:
            return "You currently have no tasks."
        return "\n".join([f"{t.id}. {t.description} - {t.status}" for t in tasks])

class UpdateTaskTool(BaseTool):
    name: str = "update_task"
    description: str = "Updates an existing task. Can update the status and/or description."
    args_schema: Type[BaseModel] = UpdateTaskInput

    def _run(self, task_id: int, status: Optional[str] = None, description: Optional[str] = None) -> str:
        service = TaskService()
        task = service.update_task(task_id, status, description)
        if task:
            return f"Task {task_id} updated. Status: {task.status}, Description: {task.description}"
        return f"Error: Task with ID {task_id} not found."

class DeleteTaskTool(BaseTool):
    name: str = "delete_task"
    description: str = "Deletes a task from the user's to-do list."
    args_schema: Type[BaseModel] = DeleteTaskInput

    def _run(self, task_id: int) -> str:
        service = TaskService()
        success = service.delete_task(task_id)
        if success:
            return f"Task {task_id} deleted successfully."
        return f"Error: Task with ID {task_id} not found."

class SummarizeTasksTool(BaseTool):
    name: str = "summarize_tasks"
    description: str = "Provides a high-level summary of the tasks, including totals, completed, and pending counts."

    def _run(self) -> str:
        service = TaskService()
        summary = service.get_summary()
        if summary["total"] == 0:
            return "You have no tasks to summarize."
        return (
            f"Total Tasks: {summary['total']}\n"
            f"Completed: {summary['completed']}\n"
            f"Pending: {summary['pending']}"
        )
