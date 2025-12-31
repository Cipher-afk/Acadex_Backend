from fastapi import APIRouter, Depends, HTTPException
from .models import SignUp, Login, User
from typing import List
from .service import UserService
from database.database_init import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from utils import create_tokens, create_token
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from dependencies.authorization import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleAuthorization,
)
from dependencies.redis_db import add_to_blacklist

router = APIRouter()
service = UserService()
REFRESH_EXPIRY = timedelta(days=2)
role_authorization = RoleAuthorization(["admin"])


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
async def get_all_users(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
    authorized: bool = Depends(role_authorization),
):
    users = await service.get_all_users(session=session)
    return users


@router.get("/get_user", response_model=User)
async def get_user_by_email(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
    authorized: bool = Depends(role_authorization),
):
    email = token_data["user"]["email"]
    user = await service.get_user_by_email(email=email, session=session)
    return user


@router.get("/refresh")
async def get_new_access_token(
    token_data: dict = Depends(RefreshTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    if token_data is None:
        raise HTTPException(status_code=403, detail="Invalid Token")
    refresh_expiry = token_data["expiry"]
    user_data = token_data = ["user"]
    if (datetime.now()).timestamp() > refresh_expiry:
        raise HTTPException(status_code=403, detail="Token Expired")
    access_token = await create_token(user_data=user_data)
    return JSONResponse(content={"access_token": access_token})


@router.get("/logout")
async def logout(token_data: dict = Depends(AccessTokenBearer())):
    jti = token_data["jti"]
    await add_to_blacklist(jti=jti)
    return JSONResponse(content={"Logged_out": "Successful"})
