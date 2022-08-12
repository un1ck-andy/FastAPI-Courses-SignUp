from pydantic import BaseModel, Field, EmailStr

class CourseSchema(BaseModel):
    id: int = Field(default=None)
    title: str = Field(...)
    description: str = Field(...)
    student_id: list = Field(...)
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Interesting course title",
                "description": "Not so boring description"
            }
        }


class StudentSchema(BaseModel):
    id: int = Field(default=None)
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Thomas Anderson",
                "email": "neo@matrix.has.you",
                "password": "weakpassword"
            }
        }

class StudentLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "neo@matrix.has.you",
                "password": "weakpassword"
            }
        }

class ApplicationsListChema(BaseModel):
    id: int = Field(default=None)
    course_id: int = Field(default=None)
    student_id: int = Field(default=None)
