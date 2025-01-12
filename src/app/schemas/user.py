from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict


class TokenData(BaseModel):
    email: Optional[str] = None


class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    uid: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class RegisterResponse(BaseModel):
    message: str
    success: bool