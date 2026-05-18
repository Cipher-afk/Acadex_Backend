from typing import List, Dict
import json
from typing import Dict
from utils import get_all_departments
from .models import SignUpModel, LoginModel
from fastapi import UploadFile, File
from database.db_models import Faculty, Department, Course, UserCourse
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_models import University
from sqlalchemy import select
from fastapi import HTTPException
from utils import hash_password, get_courses_from_course_reg, verify_password
from database.db_models import User
import asyncio
import logging

logger = logging.getLogger(__name__)


def get_abbreviation(name: str):
    name = name.lower()
    split_names = list(filter(lambda x: x != "of" and x != "and", name.split()))
    if len(split_names) > 1:
        names_abbr = "".join(
            [split_names[i][0].upper() for i in range(len(split_names))]
        )
    else:
        names_abbr = name[:3].upper()
    return names_abbr


async def get_faculty_id(
    university_name: str, faculty_name: str, session: AsyncSession
):
    statement = (
        select(Faculty)
        .join(University, Faculty.university_id == University.university_id)
        .where(
            Faculty.faculty_name == faculty_name,
            University.university_name == university_name,
        )
    )
    result = await session.execute(statement)
    faculty = result.scalars().first()
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty.faculty_id


async def get_department_id(
    department_name: str, faculty_name: str, session: AsyncSession
):
    statement = (
        select(Department)
        .join(Faculty, Department.faculty_id == Faculty.faculty_id)
        .where(
            Department.department_name == department_name,
            Faculty.faculty_name == faculty_name,
        )
    )
    result = await session.execute(statement=statement)
    department = result.scalars().first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department.department_id


async def get_university_id(university_name: str, session: AsyncSession):
    statement = select(University).where(
        University.university_name == university_name.lower()
    )
    result = await session.execute(statement=statement)
    university = result.scalars().first()
    if university is None:
        raise HTTPException(status_code=404, detail="University not found")
    return university.university_id


class UserService:

    async def add_university(self, university: str, session: AsyncSession):
        university_abbr = get_abbreviation(name=university)
        new_university = University(
            university_name=university.lower(), university_abbreviation=university_abbr
        )
        session.add(new_university)
        await session.commit()
        return new_university

    async def add_faculties(
        self, faculties: List[str], university_name: str, session: AsyncSession
    ):
        statement = select(University.university_id).where(
            university_name == university_name
        )
        result = await session.execute(statement=statement)
        university_id = result.scalars().first()
        new_faculties = []
        for faculty in faculties:
            new_faculty = Faculty(
                faculty_name=faculty.lower(), university_id=university_id
            )
            session.add(new_faculty)
            await session.commit()
            new_faculties.append(new_faculty)
        return new_faculties

    async def add_departments(
        self,
        departments: List[str],
        university_name: str,
        faculty_name: str,
        session: AsyncSession,
    ):
        faculty_id = await get_faculty_id(
            university_name=university_name.lower(),
            faculty_name=faculty_name.lower(),
            session=session,
        )
        departments_saved = []
        for department in departments:
            print(department)
            department_abbr = get_abbreviation(name=department)
            if (
                self.get_department(department_name=department.lower(), session=session)
                == None
            ):
                pass
            else:
                new_department = Department(
                    department_name=department.lower().replace("&", "and"),
                    department_abbreviation=department_abbr,
                    faculty_id=faculty_id,
                )
                session.add(new_department)
                await session.commit()
                departments_saved.append(new_department)
        return departments_saved

    async def add_courses(
        self,
        courses_data: Dict,
        faculty_name: str,
        department_name: str,
        level: int,
        session: AsyncSession,
    ):
        department_id = await get_department_id(
            department_name=department_name, faculty_name=faculty_name, session=session
        )
        courses = []
        logger.info(courses_data["course_code"])
        for i, course_code in enumerate(courses_data["course_code"]):
            course_title = courses_data["course_title"][i]
            credit_unit = courses_data["credit_unit"][i]
            new_course = Course(
                course_code=course_code,
                course_title=course_title,
                credit_unit=int(credit_unit),
            )
            new_course.course_id = (
                course_code.replace(" ", "_")
                if "FUO" in course_code
                else f"FUO_{course_code}"
            )
            new_course.level = level
            new_course.department_id = department_id
            session.add(new_course)
            await session.commit()
            courses.append(new_course)
        return courses

    async def get_department(self, department_name: str, session: AsyncSession):
        statement = select(Department).where(
            department_name == Department.department_name
        )
        result = await session.execute(statement=statement)
        department = result.scalars().first()
        return department

    async def get_all_departments(self, session: AsyncSession):
        statement = select(Department)
        results = await session.execute(statement=statement)
        departments = results.scalars().all()
        return departments

    async def get_faculty(self, faculty_name: str, session: AsyncSession):
        statement = select(Faculty).where(faculty_name == Faculty.faculty_name)
        result = await session.execute(statement=statement)
        faculty = result.scalars().first()
        return faculty

    async def get_faculty_departments(faculty_id: int, session: AsyncSession):
        statement = select(Department).where(faculty_id == Department.faculty_id)
        results = await session.execute(statement=statement)
        faculty_departments = results.scalars().all()
        return faculty_departments

    async def link_users_to_courses(email: str, course_id: str, session: AsyncSession):
        new_user_course = UserCourse(user_id=email, course_id=course_id)
        session.add(new_user_course)
        await session.commit()

    async def create_user(
        self,
        signup_model: SignUpModel,
        course_reg_contents: bytes,
        session: AsyncSession,
    ):
        signup_data = signup_model.model_dump()
        password_hash = hash_password(signup_data["password"])
        university_name = signup_data["university_name"].lower()
        faculty_name = signup_data["faculty_name"].lower()
        department_name = signup_data["department_name"].lower()
        print(signup_data["level"])
        new_user = User(**signup_data)
        new_user.level = signup_data["level"]
        new_user.password_hash = password_hash
        new_user.university_id = await get_university_id(
            university_name=university_name, session=session
        )
        new_user.faculty_id = await get_faculty_id(
            university_name=university_name, faculty_name=faculty_name, session=session
        )
        new_user.department_id = await get_department_id(
            department_name=department_name, faculty_name=faculty_name, session=session
        )
        if (
            await self.get_user_by_email(signup_data["email"], session=session)
            is not None
        ):
            raise HTTPException(
                status_code=403, detail="User Already Exists Try Logging in"
            )
        courses_data = await asyncio.to_thread(
            get_courses_from_course_reg, course_reg_contents
        )
        logger.info(courses_data)
        session.add(new_user)
        courses = await self.add_courses(
            courses_data=courses_data,
            faculty_name=faculty_name,
            department_name=department_name,
            level=signup_data["level"],
            session=session,
        )
        await session.commit()
        return new_user, courses

    async def login(self, login_data: LoginModel, session: AsyncSession):
        login_info = login_data.model_dump()
        credential = login_info["credential"]
        password = login_info["password"]
        if "@" in credential:
            user = await self.get_user_by_email(email=credential, session=session)
        else:
            user = await self.get_user_by_matric_number(
                matric_number=credential, session=session
            )
        if user is None:
            raise HTTPException(
                status=404, detail="User Not Found consider signing up".title()
            )
        password_hash = user.password_hash
        if not verify_password(password=password, password_hash=password_hash):
            raise HTTPException(status_code=403, detail="Password Incorrect")
        return user

    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(email == User.email)
        result = await session.execute(statement=statement)
        user = result.scalars().first()
        return user

    async def get_user_by_matric_number(
        self, matric_number: str, session: AsyncSession
    ):
        statement = select(User).where(User.matric_number == matric_number)
        result = await session.execute(statement=statement)
        user = result.scalars().first()
        return user

    async def reset_password():
        pass

    async def delete_user():
        pass

    async def update_user(self, user: User, info: Dict, session: AsyncSession):
        for key, value in info.items():
            setattr(user, key, value)
        await session.commit()
        return {"Updated": "Successful"}


if __name__ == "__main__":
    print(get_abbreviation("Federal University Of Otueke"))
