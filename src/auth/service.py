from sqlalchemy.ext.asyncio import AsyncSession
from .models import SignUp, Login, User
from .db_models import Users
from utils import hash_password


class UserService:
    async def add_user(user: SignUp, session: AsyncSession):
        user_data = user.model_dump()
        hashed_password = hash_password(user_data["password"])
        new_user = Users(**user_data)
        new_user.password_hash = hashed_password
        session.add(new_user)
        await session.commit()
        return new_user
