from fastapi import FastAPI
from database.database_init import init_db
from auth.routes import router as auth_router
from fastapi.staticfiles import StaticFiles
from middleware import register_middleware


async def lifespan(app: FastAPI):
    print("Server starting....")
    await init_db()
    yield
    print("Server ending....")


app = FastAPI(title="Acadex", lifespan=lifespan)
register_middleware(app=app)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router=auth_router, prefix="/auth", tags=["auth"])
# app.include_router(router=course_router, prefix="/courses", tags=["Courses"])
# app.include_router(router=notes_router, prefix="/notes", tags=["Notes"])
