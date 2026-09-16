from backend.repositories.task_repo import TaskRepository
from backend.config.database_config import SessionLocal

class TaskService:
    def add_task(self, description: str):
        db = SessionLocal()
        try:
            repo = TaskRepository(db)
            return repo.add_task(description)
        finally:
            db.close()

    def get_all_tasks(self):
        db = SessionLocal()
        try:
            repo = TaskRepository(db)
            return repo.get_all_tasks()
        finally:
            db.close()

    def update_task(self, task_id: int, status: str = None, description: str = None):
        db = SessionLocal()
        try:
            repo = TaskRepository(db)
            return repo.update_task(task_id, status, description)
        finally:
            db.close()

    def delete_task(self, task_id: int) -> bool:
        db = SessionLocal()
        try:
            repo = TaskRepository(db)
            return repo.delete_task(task_id)
        finally:
            db.close()

    def get_summary(self) -> dict:
        db = SessionLocal()
        try:
            repo = TaskRepository(db)
            return repo.get_summary()
        finally:
            db.close()
