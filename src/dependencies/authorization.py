from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils import decode_token
from fastapi import HTTPException, Depends
from fastapi.requests import Request
from .redis_db import is_in_blacklist
from sqlalchemy.ext.asyncio import AsyncSession
from database.database_init import get_session
from auth.service import UserService
from typing import List
from auth.db_models import Users

service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(
        self, *, bearerFormat=None, scheme_name=None, description=None, auto_error=True
    ):
        super().__init__(
            bearerFormat=bearerFormat,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request):
        cred = await super().__call__(request)
        token = cred.credentials
        token_data = await decode_token(token)
        if token_data is None:
            raise HTTPException(status_code=403, detail="Invalid Token")

        self.verify_token(token_data)
        jti = token_data["jti"]
        print(jti)
        if await is_in_blacklist(jti):
            raise HTTPException(status_code=403, detail="Token is invalid Login again")

        return token_data

    def verify_token(self, token_data):
        raise NotImplementedError()


class AccessTokenBearer(TokenBearer):
    def verify_token(self, token_data: str):
        if token_data["refresh"]:
            raise HTTPException(status_code=403, detail="Access Token Required")


class RefreshTokenBearer(TokenBearer):
    def verify_token(self, token_data: str):
        if not token_data["refresh"]:
            raise HTTPException(status_code=403, detail="Refresh Token Required")


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
):
    email = token_data["user"]["email"]
    user = await service.get_user_by_email(email=email, session=session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


class RoleAuthorization:
    def __init__(self, roles: List[str]):
        self.roles = roles

    async def __call__(self, user: Users = Depends(get_current_user)):
        if user.role not in self.roles:
            raise HTTPException(status_code=403, detail="Authorization Error")
        return True
