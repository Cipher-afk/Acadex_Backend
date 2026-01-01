from pydantic import BaseModel
from typing import List, Optional
from auth.db_models import Users
from notes.db_models import Notes


class Course(BaseModel):
    course_code: str
    course_title: str
    # lecturers: List[str]
    level: int
    department: str
    grade_unit: int


class CourseResponse(Course):
    user: Optional["Users"]
    notes: List["Notes"]


class UpdateCourse(Course):
    course_code: str
    course_title: str
