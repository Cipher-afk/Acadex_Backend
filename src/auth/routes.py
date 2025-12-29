from fastapi import APIRouter
from .models import SignUp, Login, User
from typing import List

router = APIRouter()


@router.post("/signup", response_model=User)
async def create_account(user: SignUp):
    pass


@router.post("/login")
async def login_to_account(user: Login):
    pass


@router.get("/get_all_users", response_model=List[User])
async def get_all_users():
    pass


@router.get("/get_user", response_model=User)
async def get_user_by_email():
    pass
