from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
import uuid


class Notes(SQLModel, table=True):
    note_id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, nullable=False, default=uuid.uuid4(), primary_key=True
        )
    )
    course_code: str = Field
    file_name: str
    description: str
    department: str
    level: int
    file_url: str = Field(default="URL")
    file_type: str
    date_uploaded: datetime = Field(sa_column=Column(pg.DATE, default=datetime.now()))
    uploaded_by: str
