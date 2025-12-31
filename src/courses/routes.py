from fastapi import APIRouter, Depends
from .models import Course, CourseResponse, UpdateCourse
from typing import List
from .service import CoursesService
from sqlalchemy.ext.asyncio import AsyncSession
from database.database_init import get_session
from dependencies.authorization import AccessTokenBearer

router = APIRouter()
service = CoursesService()


@router.post("/add_course")
async def add_course(
    course: Course,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
):
    new_course = await service.add_course(course, session)
    return new_course


@router.get("/view_course", response_model=List[CourseResponse])
async def view_course(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
):
    department = token_data["user"]["department"]
    departmental_courses = await service.get_course_by_department(department, session)
    return departmental_courses


@router.get("/view_all_courses", response_model=List[CourseResponse])
async def view_courses(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
):
    courses = await service.get_courses(session)
    return courses


@router.patch("/update_course")
async def update_course(updated_course: UpdateCourse):
    pass


# @router.post("/upload_notes")
# async def add_notes():
#     pass


# @router.get("/get_notes")
# async def get_notes():
#     pass


# @router.get("/download_notes")
# async def download_notes():
#     pass
