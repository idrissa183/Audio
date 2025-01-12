from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict


class TokenData(BaseModel):
    email: Optional[str] = None
    uid: Optional[int] = None


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

# Schémas pour les sessions
class SessionBase(BaseModel):
    session_name: str

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: int
    user_uid: int
    created_at: datetime

    class Config:
        from_attributes = True

# Schémas pour les messages
class MessageBase(BaseModel):
    message: str

class MessageCreate(MessageBase):
    session_id: int

class MessageResponse(MessageBase):
    id: int
    session_id: int
    sender: str
    created_at: datetime

    class Config:
        from_attributes = True
