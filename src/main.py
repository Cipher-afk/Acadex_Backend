from fastapi import FastAPI
from database.database_init import init_db
from courses.routes import router as course_router
from notes.routes import router as notes_router
from auth.routes import router as auth_router


async def lifespan(app: FastAPI):
    print("Server starting....")
    await init_db()
    yield
    print("Server ending....")


app = FastAPI(title="Acadex", lifespan=lifespan)
app.include_router(router=auth_router, prefix="/auth", tags=["auth"])
app.include_router(router=course_router, prefix="/courses", tags=["Courses"])
app.include_router(router=notes_router, prefix="/notes", tags=["Notes"])
