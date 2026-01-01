from sqlmodel import SQLModel, Field, Column, Relationship
from typing import Optional, List
import sqlalchemy.dialects.postgresql as pg
from auth import db_models
from notes import db_models


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
    user_id: str = Field(foreign_key="users.email")
    user: Optional["db_models.Users"] = Relationship(
        back_populates="courses", sa_relationship_kwargs={"lazy": "selectin"}
    )
    notes: List["db_models.Notes"] = Relationship(
        back_populates="courses", sa_relationship_kwargs={"lazy": "selectin"}
    )
