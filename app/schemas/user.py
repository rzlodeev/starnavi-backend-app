from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    auto_respond_to_comments: Optional[bool] = None
    auto_respond_time: Optional[int] = None


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    auto_respond_to_comments: bool
    auto_respond_time: int | None

    class Config:
        orm_mode = True


class UserProfile(BaseModel):
    id: int
    user_id: int
    bio: str | None
    profile_picture: str | None

    class Config:
        orm_mode = True
