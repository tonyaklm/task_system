from pydantic import BaseModel


class NewRight(BaseModel):
    access_user_login: str
    task_id: int
    access_mode: int
