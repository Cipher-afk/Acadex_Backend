from pydantic import BaseModel
from typing import List


class Course(BaseModel):
    course_code: str
    course_title: str
    # lecturers: List[str]
    level: int
    department: str
    grade_unit: int


class CourseResponse(Course):
    pass


class UpdateCourse(Course):
    pass
