from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import SQLModel
from sqlalchemy.orm import sessionmaker
from config import settings

url = settings.DATABASE_URL
engine = create_async_engine(url=url, echo=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


asyncsession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    async with asyncsession() as session:
        yield session
