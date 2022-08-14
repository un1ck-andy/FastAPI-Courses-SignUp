from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class CourseSchema(BaseModel):
    course_id: int = Field(default=None)
    title: str = Field(...)
    description: str = Field(...)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "title": "Interesting course title",
                "description": "Not so boring description",
            }
        }


class CourseUpdateSchema(BaseModel):
    title: Optional[str] = Field(...)
    description: Optional[str] = Field(...)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "title": "Interesting course title",
                "description": "Not so boring description",
            }
        }


class StudentSchema(BaseModel):
    student_id: int = Field(default=None)
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "fullname": "Thomas Anderson",
                "email": "neo@matrix.has.you",
                "password": "weakpassword",
            }
        }


class StudentListSchema(BaseModel):
    student_id: int = Field(default=None)
    fullname: str = Field(...)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "fullname": "Thomas Anderson",
            }
        }


class StudentLoginSchema(BaseModel):
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)

    class Config:
        schema_extra = {
            "example": {
                "email": "neo@matrix.has.you",
                "password": "weakpassword",
            }
        }


class CourseSignUpSchema(BaseModel):
    course_id: int = Field(default=None)
    student_id: int = Field(default=None)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "course_id": "1",
                "student_id": "2",
            }
        }
