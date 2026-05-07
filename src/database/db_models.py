from sqlmodel import SQLModel, Field, Column, Relationship
from enum import Enum
import sqlalchemy.dialects.postgresql as pg
from typing import List


class RepStatus(str, Enum):
    pending = "pending"
    revoked = "revoked"
    verified = "verified"


class User(SQLModel, table=True):
    email: str = Field(
        sa_column=Column(pg.VARCHAR, unique=True, primary_key=True, nullable=False)
    )
    matric_number = Field(sa_column=Column(pg.VARCHAR, unique=True, nullable=False))
    is_verified: bool = Field(sa_column=Column(pg.BOOLEAN, default=False))
    is_admin: bool = Field(sa_column=Column(pg.BOOLEAN, default=False))
    is_course_rep: bool = Field(sa_column=Column(pg.BOOLEAN, default=False))
    rep_status: RepStatus | None = Field(sa_column=Column(pg.VARCHAR, default=None))
    university_name: str = Field(foreign_key="university.university_name")
    department_name: str = Field(foreign_key="department.department_name")
    courses: List["Course"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )


class University(SQLModel, table=True):
    university_name: str = Field(
        sa_column=Column(pg.VARCHAR, primary_key=True, unique=True, nullable=False)
    )
    university_abbreviation = Field(sa_column=Column(pg.VARCHAR, unique=True))
    departments: List["Department"] = Relationship(
        back_populates="university", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Department(SQLModel, table=True):
    department_name: str = Field(
        sa_column=Column(pg.VARCHAR, primary_key=True, unique=True)
    )
    department_abbreviation = Field(sa_column=Column(pg.VARCHAR, unique=True))
    university_name: str = Field(
        foreign_key="school.university_name",
    )
    university: University = Relationship(
        back_populates="departments", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Course(SQLModel, table=True):
    course_id: str = Field(
        sa_column=Column(pg.VARCHAR, primary_key=True, unique=True)
    )  # CourseCode_UniAbbr
    course_code: str
    course_title: str
    credit_unit: int
    department_name: str = Field(foreign_key="department.department_name")
    university_name: str = Field(foreign_key="university.university_name")
    user: User = Relationship(
        back_populates="courses", sa_relationship_kwargs={"lazy": "selectin"}
    )
