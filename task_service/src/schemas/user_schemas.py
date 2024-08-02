from pydantic import BaseModel


class UserRegistration(BaseModel):
    login: str
    password: str
    first_name: str
    second_name: str


class UserAuthentication(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
