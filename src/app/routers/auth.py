from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from src.app.db.session import get_db
from src.app.models.user import User
from src.app.utils.authentication import create_access_token, create_refresh_token, get_password, verify_password
from src.app.schemas.user import Token, UserCreate, RegisterResponse
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

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
              },
        expires_delta=timedelta(minutes=30)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email,
              "firstname": user.firstname,
              "lastname": user.lastname,
              "username": user.username,
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
        }
    }


@router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}




# @router.get("/auth/google")
# async def login_or_register_with_google():
#     return {
#         "url": f"https://accounts.google.com/o/oauth2/v2/auth?"
#         f"client_id={GOOGLE_CLIENT_ID}&"
#         f"response_type=code&"
#         f"scope=openid email profile&"
#         f"redirect_uri={FRONTEND_URL}/auth/google/callback"
#     }



# @router.post("/auth/google/callback")
# async def google_callback(code: str, db: Session = Depends(get_db)):
#     token_url = "https://oauth2.googleapis.com/token"
#     data = {
#         "code": code,
#         "client_id": GOOGLE_CLIENT_ID,
#         "client_secret": GOOGLE_CLIENT_SECRET,
#         "redirect_uri": f"{FRONTEND_URL}/auth/google/callback",
#         "grant_type": "authorization_code"
#     }
#     response = requests.post(token_url, data=data)
#     if not response.ok:
#         raise HTTPException(status_code=400, detail="Failed to get Google token")
    
    # google_token = response.json()["id_token"]
    # google_info = await verify_google_token(google_token)
    # if not google_info:
    #     raise HTTPException(status_code=400, detail="Failed to verify Google token")
    
    # user = await get_user_by_google_sub(google_info["sub"], db)
    # if not user:
    #     user = await create_user_from_google_infos(google_info, db)
    
    # access_token = create_access_token(
    #     data={"sub": user.email},
    #     expires_delta=timedelta(minutes=30)
    # )
    # refresh_token = create_refresh_token(
    #     data={"sub": user.email}
    # )
    
    # return {
    #     "access_token": access_token,
    #     "refresh_token": refresh_token,
    #     "token_type": "bearer"
    # }



# @router.get("/auth/github")
# async def login_or_register_with_github():
#     return {
#         "url": f"https://github.com/login/oauth/authorize?"
#         f"client_id={GITHUB_CLIENT_ID}&"
#         f"scope=user:email"
#     }



# @router.post("/auth/github/callback")
# async def github_callback(code: str, db: Session = Depends(get_db)):
#     token_url = "https://github.com/login/oauth/access_token"
#     data = {
#         "client_id": GITHUB_CLIENT_ID,
#         "client_secret": GITHUB_CLIENT_SECRET,
#         "code": code
#     }
#     headers = {"Accept": "application/json"}
#     response = requests.post(token_url, data=data, headers=headers)
#     if not response.ok:
#         raise HTTPException(status_code=400, detail="Failed to get GitHub token")
    
#     github_token = response.json()["access_token"]
    # github_info, emails_info = await get_github_user_info(github_token)
    
    # if not github_info or not emails_info:
    #     raise HTTPException(status_code=400, detail="Failed to get GitHub user info")
    
    # user = await get_user_by_github_sub(str(github_info["id"]), db)
    # if not user:
    #     user = await create_user_from_github_infos(github_info, emails_info, db)
    
    # access_token = create_access_token(
    #     data={"sub": user.email},
    #     expires_delta=timedelta(minutes=30)
    # )
    # refresh_token = create_refresh_token(
    #     data={"sub": user.email}
    # )
    
    # return {
    #     "access_token": access_token,
    #     "refresh_token": refresh_token,
    #     "token_type": "bearer"
    # }
