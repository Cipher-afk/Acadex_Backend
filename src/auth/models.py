from pydantic import (
    BaseModel,
    EmailStr,
)
from fastapi import HTTPException

LEVELS = list(range(100, 800))


class SignUpModel(BaseModel):
    email: EmailStr
    matric_number: str
    username: str
    level: int
    password: str
    university_name: str
    faculty_name: str
    department_name: str


class LoginModel(BaseModel):
    credential: str
    password: str
