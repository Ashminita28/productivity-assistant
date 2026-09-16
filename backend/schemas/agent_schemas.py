from pydantic import BaseModel, Field

class Intent(BaseModel):
    intent: str = Field(description="The exact category string: add_task, list_tasks, update_task, delete_task, summarize_tasks, or follow_up")

class Guardrail(BaseModel):
    is_safe: bool = Field(description="True if the prompt is safe and on-topic, False if it is malicious, toxic, or off-topic.")
    reason: str = Field(description="If unsafe, explain why. If safe, just say 'Safe'.")

class AddTask(BaseModel):
    description: str = Field(description="The description of the task to add.")

class UpdateTask(BaseModel):
    task_id: int = Field(description="The ID of the task to update.")
    status: str | None = Field(default=None, description="The new status of the task (e.g. Completed).")
    description: str | None = Field(default=None, description="The new description of the task.")

class DeleteTask(BaseModel):
    task_id: int = Field(description="The ID of the task to delete.")
