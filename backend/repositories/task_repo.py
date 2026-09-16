from sqlalchemy.orm import Session
from backend.models.task import Task
from typing import List, Dict

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_tasks(self) -> List[Task]:
        """Fetch all tasks from the database."""
        return self.db.query(Task).all()

    def add_task(self, description: str) -> Task:
        """Create a new task and save it."""
        new_task = Task(description=description, status="Pending")
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    def update_task(self, task_id: int, status: str = None, description: str = None) -> Task:
        """Update a task's status and/or description if it exists."""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task:
            if status:
                task.status = status
            if description:
                task.description = description
            self.db.commit()
            self.db.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task and return True if successful."""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False
        
    def get_summary(self) -> Dict[str, int]:
        """Return a count of completed vs pending tasks."""
        total = self.db.query(Task).count()
        completed = self.db.query(Task).filter(Task.status == "Completed").count()
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed
        }
