"""Custom domain exception classes for the Productivity Assistant."""

from typing import Optional, Any

class BaseAppException(Exception):
    """Base domain exception for the application."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details

class TaskNotFoundException(BaseAppException):
    """Raised when a requested task ID is not found."""

    def __init__(self, task_id: int):
        super().__init__(
            message=f"Task with ID '{task_id}' was not found.",
            status_code=404,
            error_code="TASK_NOT_FOUND",
        )
