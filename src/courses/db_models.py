from sqlmodel import SQLModel, Relationship, Field, Column
import sqlalchemy.dialects.postgresql as pg
from database import db_models


class Course(SQLModel, table=True):
    __tablename__ = "courses"
    course_id: str = Field(
        sa_column=Column(pg.VARCHAR, primary_key=True, unique=True)
    )  # CourseCode_UniAbbr
    course_code: str
    course_title: str
    credit_unit: int
    department_id: int = Field(foreign_key="department.department_id")
    user: "db_models.User" = Relationship(
        back_populates="courses", sa_relationship_kwargs={"lazy": "selectin"}
    )
