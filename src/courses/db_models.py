from sqlmodel import SQLModel, Field, Column
from typing import List, Sequence
import sqlalchemy.dialects.postgresql as pg
from .models import Course
import string


class Courses(SQLModel, table=True):
    __tablename__ = "courses"
    course_code: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, primary_key=True)
    )
    course_title: str
    # lecturers: = Field(sa_column=Column(pg.ARRAY(string), nullable=False))
    department: str
    level: int
    grade_unit: int
