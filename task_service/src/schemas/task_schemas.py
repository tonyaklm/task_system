from pydantic import BaseModel


class NewTask(BaseModel):
    title: str
    content: str


class UpdateTask(BaseModel):
    task_id: int
    new_title: str
    new_content: str


class TaskId(BaseModel):
    task_id: int


class Task(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
