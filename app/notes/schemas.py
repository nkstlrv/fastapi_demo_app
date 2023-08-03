from pydantic import BaseModel


class Note(BaseModel):
    title: str
    body: str


class User(BaseModel):
    username: str
    email: str
    password: str