from fastapi import APIRouter, Depends, HTTPException
from .models import SignUp, Login, User
from typing import List
from .service import UserService
from database.database_init import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from utils import create_tokens
from datetime import timedelta
from fastapi.responses import JSONResponse

router = APIRouter()
service = UserService()
REFRESH_EXPIRY = timedelta(days=2)


@router.post("/signup", response_model=User)
async def create_account(user: SignUp, session: AsyncSession = Depends(get_session)):
    try:
        new_user = await service.add_user(user=user, session=session)
        if new_user is not None:
            user_data = {
                "email": user.email,
                "department": user.department,
                "matric_number": user.matric_number,
            }
            response = await create_tokens(user_data=user_data)
            return response
    except Exception as e:
        await session.rollback()
        print(e)


@router.post("/login")
async def login_to_account(
    login_data: Login, session: AsyncSession = Depends(get_session)
):
    user = await service.login(login_data=login_data, session=session)
    if user is not None:
        user_data = {
            "email": user.email,
            "department": user.department,
            "matric_number": user.matric_number,
        }
        response = await create_tokens(user_data=user_data)
        return response

    raise HTTPException(status_code=404, detail="User Not Found")


@router.get("/get_all_users", response_model=List[User])
async def get_all_users(session: AsyncSession = Depends(get_session)):
    users = await service.get_all_users(session=session)
    return users


@router.get("/get_user", response_model=User)
async def get_user_by_email(email: str, session: AsyncSession = Depends(get_session)):
    user = await service.get_user_by_email(email=email, session=session)
    return user
