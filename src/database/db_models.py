from sqlmodel import SQLModel, Field, Column, Relationship
from enum import Enum
import sqlalchemy.dialects.postgresql as pg
from typing import List


class RepStatus(str, Enum):
    pending = "pending"
    revoked = "revoked"
    verified = "verified"


class University(SQLModel, table=True):
    __tablename__ = "university"
    university_id: int = Field(
        sa_column=Column(pg.INTEGER, primary_key=True, autoincrement=True)
    )
    university_name: str = Field(
        sa_column=Column(pg.VARCHAR, unique=True, nullable=False)
    )
    university_abbreviation: str = Field(sa_column=Column(pg.VARCHAR, unique=True))
    # departments: List["Department"] = Relationship(
    #     back_populates="university", sa_relationship_kwargs={"lazy": "selectin"}
    # )


class Faculty(SQLModel, table=True):
    __tablename__ = "faculty"
    faculty_id: int = Field(
        sa_column=Column(pg.INTEGER, primary_key=True, autoincrement=True)
    )
    faculty_name: str = Field(sa_column=Column(pg.VARCHAR))
    university_id: int = Field(foreign_key="university.university_id")
    departments: List["Department"] = Relationship(
        back_populates="faculty", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Department(SQLModel, table=True):
    __tablename__ = "department"
    department_id: int = Field(
        sa_column=Column(pg.INTEGER, primary_key=True, autoincrement=True)
    )
    department_name: str = Field(sa_column=Column(pg.VARCHAR, unique=True))
    department_abbreviation: str = Field(sa_column=Column(pg.VARCHAR))
    faculty_id: int = Field(foreign_key="faculty.faculty_id")
    faculty: Faculty = Relationship(
        back_populates="departments", sa_relationship_kwargs={"lazy": "selectin"}
    )
    # university: University = Relationship(
    #     back_populates="departments", sa_relationship_kwargs={"lazy": "selectin"}
    # )


class User(SQLModel, table=True):
    __tablename__ = "users"
    email: str = Field(
        sa_column=Column(pg.VARCHAR, unique=True, primary_key=True, nullable=False)
    )
    matric_number: str = Field(
        sa_column=Column(pg.VARCHAR, unique=True, nullable=False)
    )
    username: str
    level: int
    password_hash: str
    is_verified: bool = Field(sa_column=Column(pg.BOOLEAN, default=False))
    is_admin: bool = Field(sa_column=Column(pg.BOOLEAN, default=False))
    is_course_rep: bool = Field(sa_column=Column(pg.BOOLEAN, default=False))
    rep_status: RepStatus | None = Field(sa_column=Column(pg.VARCHAR, default=None))
    faculty_id: int = Field(foreign_key="faculty.faculty_id")
    university_id: int = Field(foreign_key="university.university_id")
    department_id: int = Field(foreign_key="department.department_id")


class Course(SQLModel, table=True):
    __tablename__ = "courses"
    course_id: str = Field(
        sa_column=Column(pg.VARCHAR, primary_key=True, unique=True)
    )  # CourseCode_UniAbbr
    course_code: str
    course_title: str
    credit_unit: int
    level: int = Field(nullable=True)
    department_id: int = Field(foreign_key="department.department_id")


class UserCourse(SQLModel, table=True):
    id: int = Field(sa_column=Column(pg.INTEGER, autoincrement=True, primary_key=True))
    user_id: str = Field(foreign_key="users.email")
    course_id: str = Field(foreign_key="courses.course_id")
