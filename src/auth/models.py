from pydantic import BaseModel, EmailStr, field_validator, Field


class SignUp(BaseModel):
    full_name: str
    email: EmailStr
    matric_number: str = Field(pattern=r"FUO\d{2}\[a-zA-Z]{3}\d{5}$")
    department: str
    level: int

    @field_validator(level)
    def validator(cls, value):
        levels = [100, 200, 300, 400, 500, 600, 700]
        if value not in levels:
            raise Exception("Please input a legit level")
        return value

    password: str = Field(min_length=6)


class Login(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    full_name: str
    email: EmailStr
    matric_number: str
    department: str
    level: int
