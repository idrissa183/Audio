from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from jose import jwt, JWTError
from src.app.db.session import get_db
from sqlalchemy.orm import Session

from src.app.models.user import User
from src.app.schemas.user import TokenData

load_dotenv()


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto" 
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_password(password: str) -> str :
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("TOKEN_SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        os.getenv("TOKEN_SECRET_KEY"),
        algorithm=os.getenv("ALGORITHM")
    )
    return encoded_jwt


def decode_token (token: str):
    try:
        payload = jwt.decode(
            token,
            os.getenv("TOKEN_SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM")]
        )
        return payload
    except JWTError:
        return None
    

def encode_token (payload: dict, secret_key: str = os.getenv("TOKEN_SECRET_KEY")):
    return jwt.encode (
        payload,
        secret_key,
        algorithm=os.getenv("ALGORITHM")
    )


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception
        email: str = payload.get("sub")
        uid: int = payload.get("uid")
        if email is None or uid is None:
            raise credentials_exception
        token_data = TokenData(email=email, uid=uid)
    except:
        raise credentials_exception

    user = db.query(User).filter(
        token_data.email == User.email,
        token_data.uid == User.uid
    ).first()
    if user is None:
        raise credentials_exception
    return user



# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = decode_token(token)
#         if payload is None:
#             raise credentials_exception
#         email: str = payload.get("sub")
#         if email is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#
#     user = db.query(User).filter(email == User.email).first()
#     if user is None:
#         raise credentials_exception
#     return user





# def get_user_by_google_sub(google_sub: str, db: Session):
#     return db.query(User).filter(User.google_sub == google_sub).first()
#
#
# def get_user_by_github_sub(github_sub: str, db: Session):
#     return db.query(User).filter(User.github_sub == github_sub).first()
#
#
# def create_user_from_google_infos(google_info: dict, db: Session):
#     user = User(
#         email=google_info.get("email"),
#         firstname=google_info.get("given_name", ""),
#         lastname=google_info.get("family_name", ""),
#         google_sub=google_info.get("sub"),
#         profile_picture=google_info.get("picture")
#     )
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user
#
#
# def create_user_from_github_infos(github_info: dict, emails_info: list, db: Session):
#     pass
