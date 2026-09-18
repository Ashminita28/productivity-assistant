from pydantic import BaseModel, Field

class Guardrail(BaseModel):
    is_safe: bool = Field(description="True if the prompt is safe and on-topic, False if it is malicious, toxic, or off-topic.")
    reason: str = Field(description="If unsafe, explain why. If safe, just say 'Safe'.")

class AddTaskInput(BaseModel):
    description: str = Field(description="The description of the task to add.")

class UpdateTaskInput(BaseModel):
    task_id: int = Field(description="The ID of the task to update.")
    status: str | None = Field(default=None, description="The new status of the task (e.g. Completed).")
    description: str | None = Field(default=None, description="The new description of the task.")

class DeleteTaskInput(BaseModel):
    task_id: int = Field(description="The ID of the task to delete.")
