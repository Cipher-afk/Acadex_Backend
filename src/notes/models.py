from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from auth.db_models import Users
from courses.db_models import Courses


class NoteResponse(BaseModel):
    file_name: str
    course_code: str
    # add page count
    date_uploaded: datetime
    uploaded_by: str
    courses: List["Courses"]


class Note(BaseModel):
    course_code: str
    level: str
    department: str
    uploaded_by: str
