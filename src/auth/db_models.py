from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from typing import List
from courses import db_models
from notes import db_models


class Users(SQLModel, table=True):
    __tablename__ = "users"
    email: str = Field(
        sa_column=Column(pg.VARCHAR, unique=True, nullable=False, primary_key=True)
    )
    full_name: str
    matric_number: str
    department: str
    level: int
    password_hash: str
    role: str = Field(sa_column=Column(pg.VARCHAR, server_default="user"))
    is_verified: str = Field(sa_column=Column(pg.VARCHAR, server_default="false"))
    courses: List["db_models.Courses"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    # notes: List["db_models.Notes"] = Relationship(
    #     back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    # )
