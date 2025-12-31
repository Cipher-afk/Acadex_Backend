from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg


class Users(SQLModel, table=True):
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
