from fastapi import FastAPI
from database.database_init import init_db
from courses.routes import router as course_router


async def lifespan(app: FastAPI):
    print("Server starting....")
    await init_db()
    yield
    print("Server ending....")


app = FastAPI(title="Acadex", lifespan=lifespan)
app.include_router(router=course_router, prefix="/courses")
