from sqlalchemy.ext.asyncio import AsyncSession
from .models import SignUp, Login, User
from .db_models import Users
from utils import hash_password, verify_password
from sqlalchemy import select
from fastapi import HTTPException


class UserService:
    async def add_user(self, user: SignUp, session: AsyncSession):
        user_data = user.model_dump()
        hashed_password = hash_password(user_data["password"])
        new_user = Users(**user_data)
        new_user.password_hash = hashed_password
        session.add(new_user)
        await session.commit()
        return new_user

    async def login(self, login_data: Login, session: AsyncSession):
        user_data = login_data.model_dump()
        email = user_data["email"]
        password = user_data["password"]
        user = await self.get_user_by_email(email=email, session=session)
        if user is None:
            raise HTTPException(
                status_code=404, detail="Email incorrect User not found"
            )
        verified = verify_password(password, user.password_hash)
        if not verified:
            raise HTTPException(status_code=403, detail="Incorrect Password")
        return user

    async def get_all_users(self, session: AsyncSession):
        statement = select(Users)
        result = await session.execute(statement=statement)
        users = result.scalars().all()
        return users

    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(Users).where(Users.email == email)
        result = await session.execute(statement=statement)
        user = result.scalars().first()
        return user

    async def update_user_info(self, email: str, info: dict, session: AsyncSession):
        user = await self.get_user_by_email(email=email, session=session)
        if user is None:
            raise HTTPException(
                status_code=404, detail="Email incorrect User not found"
            )
        for key, value in user.items():
            setattr(user, key, value)
        await session.commit()
        return user

    async def delete_user(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email=email, session=session)
        if user is None:
            raise HTTPException(
                status_code=404, detail="Email incorrect User not found"
            )
        session.delete(user)
        await session.commit()
        return {"message": "User deleted successfully"}
