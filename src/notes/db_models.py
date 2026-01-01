from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
import uuid
from typing import List, Optional
from auth import db_models
from courses import db_models


class Notes(SQLModel, table=True):
    __tablename__ = "notes"
    note_id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, nullable=False, default=uuid.uuid4(), primary_key=True
        )
    )
    course_code: str = Field(foreign_key="courses.course_code")
    file_name: str
    description: str
    department: str
    level: int
    file_url: str = Field(default="URL")
    file_type: str
    date_uploaded: datetime = Field(sa_column=Column(pg.DATE, default=datetime.now()))
    uploaded_by: str
    # user: Optional["db_models.Users"] = Relationship(
    #     back_populates="notes", sa_relationship_kwargs={"lazy": "selectin"}
    # )
    courses: List["db_models.Courses"] = Relationship(
        back_populates="notes", sa_relationship_kwargs={"lazy": "selectin"}
    )
