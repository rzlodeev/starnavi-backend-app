from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserProfile(BaseModel):
    id: int
    user_id: int
    bio: str | None
    profile_picture: str | None

    class Config:
        orm_mode = True
