from pydantic import BaseModel
from datetime import datetime


class NoteResponse(BaseModel):
    file_name: str
    course_code: str
    # add page count
    date_uploaded: datetime
    uploaded_by: str
