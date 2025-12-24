from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime


class Notes(SQLModel, table=True):
    course_code: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, primary_key=True)
    )
    file_name: str
    department: str
    level: int
    date_uploaded: datetime = Field(sa_column=Column(pg.DATE, default=datetime.now()))
    uploaded_by: str
