from pydantic import BaseModel
from datetime import datetime


class NoteResponse(BaseModel):
    file_name: str
    course_code: str
    # add page count
    date_uploaded: datetime
    uploaded_by: str


class Note(BaseModel):
    course_code: str
    level: str
    department: str
    uploaded_by: str
