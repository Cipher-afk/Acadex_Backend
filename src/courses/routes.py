from fastapi import APIRouter, Depends
from .models import Course, CourseResponse, UpdateCourse
from typing import List
from .service import CoursesService
from sqlalchemy.ext.asyncio import AsyncSession
from database.database_init import get_session
from dependencies.authorization import AccessTokenBearer, RoleAuthorization

router = APIRouter()
service = CoursesService()
role_authorization = RoleAuthorization(["admin"])


@router.post(
    "/add_course",
)
async def add_course(
    course: Course,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
):
    email = token_data["user"]["email"]
    new_course = await service.add_course(email, course, session)
    return new_course


@router.get("/get_user_courses", response_model=List[CourseResponse])
async def view_course(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
):
    user_id = token_data["user"]["email"]
    user_courses = await service.get_course_by_user_id(user_id, session)
    return user_courses


@router.get("/get_all_courses", response_model=List[CourseResponse])
async def view_courses(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
    # authorized: bool = Depends(role_authorization),
):
    courses = await service.get_courses(session)
    return courses


@router.patch("/update_course", response_model=CourseResponse)
async def update_course(
    course_code: str,
    updated_course: UpdateCourse,
    token_data: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    updated_data = updated_course.model_dump()
    course = await service.get_course_by_course_code(
        course_code=course_code, session=session
    )
    course_update = await service.update_info(
        course=course, info=updated_data, session=session
    )
    return course_update
