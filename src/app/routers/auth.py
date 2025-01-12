from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

from src.app.db.session import get_db
from src.app.models.user import User, Message
from src.app.utils.authentication import create_access_token, create_refresh_token, get_password, verify_password, \
    get_current_user, decode_token
from src.app.schemas.user import Token, UserCreate, RegisterResponse, SessionResponse, SessionCreate, MessageCreate, \
    MessageResponse
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from src.app.models.user import Session as SessionModel
load_dotenv()


router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL")


@router.post("/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
    ):
    if db.query(User).filter(user.email == User.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    hashed_password = get_password(user.password)
    db_user = User(
        email=user.email,
        password=hashed_password,
        firstname=user.firstname,
        lastname=user.lastname,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "message": "Compte créé avec succès",
        "success": True
    }


@router.post("/auth/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(form_data.username == User.email).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email,
              "firstname": user.firstname,
              "lastname": user.lastname,
              "username": user.username,
              "uid": user.uid
              },
        expires_delta=timedelta(minutes=30)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email,
              "firstname": user.firstname,
              "lastname": user.lastname,
              "username": user.username,
              "uid": user.uid
              },
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "firstname": user.firstname,
            "lastname": user.lastname,
            "username": user.username,
            "uid": user.uid
        }
    }


@router.post("/auth/refresh", response_model=Token)
async def refresh_token(
        refresh_token: str = Body(..., embed=True),
        db: Session = Depends(get_db)
):
    try:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(
            data={
                "sub": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "username": user.username,
                "uid": user.uid
            },
            expires_delta=timedelta(minutes=30)
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "firstname": user.firstname,
                "lastname": user.lastname,
                "username": user.username,
                "uid": user.uid
            }
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}



@router.post("/session", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée une nouvelle session pour l'utilisateur connecté."""
    db_session = SessionModel(
        session_name=session.session_name,
        user_uid=current_user.uid
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/session", response_model=List[SessionResponse])
async def retrieve_sessions_by_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(SessionModel).filter(SessionModel.user_uid == current_user.uid).all()
    return sessions



@router.post("/message", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Vérifier si la session appartient à l'utilisateur
    session = db.query(SessionModel).filter(
        SessionModel.id == message.session_id,
        SessionModel.user_uid == current_user.uid
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied"
        )

    db_message = Message(
        session_id=message.session_id,
        message=message.message,
        sender=current_user.username
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/message/{session_id}", response_model=List[MessageResponse])
async def retrieve_messages_by_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Vérifier si la session appartient à l'utilisateur
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_uid == current_user.uid
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied"
        )

    messages = db.query(Message).filter(Message.session_id == session_id).all()
    return messages
