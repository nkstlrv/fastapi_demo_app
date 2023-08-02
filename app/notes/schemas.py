from pydantic import BaseModel


class Note(BaseModel):
    title: str
    body: str
    created_at: str
    edited_at: str
