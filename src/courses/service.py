from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .db_models import Courses
from .models import Course as course_model
from utils import make_folder
from datetime import datetime


class CoursesService:

    async def get_courses(self, session: AsyncSession):
        statement = select(Courses).offset(10).limit(5)
        result = await session.execute(statement)
        courses = result.scalars().all()
        return courses

    async def get_course_by_user_id(self, email: str, session: AsyncSession):
        statement = select(Courses).where(email == Courses.user_id)
        result = await session.execute(statement=statement)
        course = result.scalars().all()
        return course

    async def get_course_by_course_code(self, course_code: str, session: AsyncSession):
        statement = select(Courses).where(course_code == Courses.course_code)
        result = await session.execute(statement=statement)
        course = result.scalars().first()
        return course

    async def add_course(self, email: str, course: course_model, session: AsyncSession):
        course_data = course.model_dump()
        year = datetime.now().year
        new_course = Courses(**course_data)
        new_course.user_id = email
        session.add(new_course)
        await session.commit()
        make_folder(course_data["course_code"], year=year)
        return new_course

    async def update_info(self, course: Courses, info: dict, session: AsyncSession):
        updated_course = course
        for key, value in info.items():
            setattr(updated_course, key, value)
        await session.commit()
        return updated_course
