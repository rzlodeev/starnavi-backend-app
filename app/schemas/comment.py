from pydantic import BaseModel
from datetime import datetime


class CommentCreate(BaseModel):
    content: str


class CommentUpdate(BaseModel):
    content: str


class Comment(BaseModel):
    id: int
    content: str
    created_at: datetime
    owner_id: int
    post_id: int

    class Config:
        orm_mode = True


class BlockedComment(BaseModel):
    id: int
    content: str
    created_at: datetime
    owner_id: int
    post_id: int
    blocking_reasoning: str

    class Config:
        orm_mode = True
