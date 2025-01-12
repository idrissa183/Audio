from fastapi import APIRouter

from src.app.models.user import User
from src.app.schemas.user import UserResponse, UserCreate

router = APIRouter()


@router.get("/users")
async def read_users():
    pass

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    pass

@router.get("/users/{uid}")
async def get_user_by_id():
    pass

@router.put("/users/{uid}")
async def update_user():
    pass

@router.delete("/users/{uid}")
async def delete_user():
    pass
