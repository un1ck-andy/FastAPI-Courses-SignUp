from fastapi import Body
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status

from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT
from app.db import db
from app.models import Course
from app.models import Student
from app.schemas import CourseSchema
from app.schemas import StudentLoginSchema
from app.schemas import StudentSchema


description = """
Course API helps you do awesome stuff (someday, maybe). \n
It uses PostgreSQL and SQLAlchemy + Alembic under the hood \n
with JWT for authentication.

## Courses

You can search, add, modify and delete courses.

## Students

You can search, add, modify and delete student's accounts.

"""


tags_metadata = [
    {"name": "Test", "description": "Endpoints for testing"},
    {"name": "Courses", "description": "Endpoints to work with courses"},
    {"name": "Students", "description": "Endpoints to work with students"},
]

app = FastAPI(
    openapi_tags=tags_metadata,
    title="Course subscription on FastAPI",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Andy",
        "email": "andy@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


def check_student(data: StudentLoginSchema):
    check_result = (
        db.query(Student)
        .filter(Student.email == data.email, Student.password == data.password)
        .first()
    )
    if check_result:
        return True
    return False


# route handlers
# Courses
@app.get(
    "/api/v1/courses",
    response_model=list[CourseSchema],
    status_code=status.HTTP_200_OK,
    tags=["Courses"],
)
async def get_all_courses():
    """A list of all courses"""

    courses = db.query(Course).all()
    return courses


@app.get(
    "/api/v1/courses/{id}",
    response_model=CourseSchema,
    status_code=status.HTTP_200_OK,
    tags=["Courses"],
)
async def get_single_course(id: int):
    """Find a course by ID"""
    course = db.query(Course).filter(Course.course_id == id).first()

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return course


@app.post(
    "/api/v1/courses",
    dependencies=[Depends(JWTBearer())],
    status_code=status.HTTP_201_CREATED,
    response_model=CourseSchema,
    tags=["Courses"],
)
async def add_course(course: CourseSchema):
    """Add a new course"""
    db_course = db.query(Course).filter(Course.title == course.title).first()

    if db_course is not None:
        raise HTTPException(
            status_code=400, detail="Course with the same title already exists"
        )

    new_course = Course(
        title=course.title,
        description=course.description,
    )

    db.add(new_course)
    db.commit()
    return new_course


@app.get(
    "/api/v1/students",
    response_model=list[StudentSchema],
    status_code=status.HTTP_200_OK,
    tags=["Test"],
)
async def fetch_students():
    """Show all students list"""
    students = db.query(Student).all()
    return students


@app.post(
    "/api/v1/students/signup",
    status_code=status.HTTP_201_CREATED,
    tags=["Students"],
)
async def signup_student(student: StudentSchema = Body(...)):
    """Add a new user"""
    db_student = (
        db.query(Student).filter(Student.email == student.email).first()
    )

    if db_student is not None:
        raise HTTPException(
            status_code=400, detail="User with the same email already exists"
        )

    new_student = Student(
        fullname=student.fullname,
        email=student.email,
        password=student.password,
    )

    db.add(new_student)
    db.commit()
    return signJWT(student.email)


@app.post(
    "/api/v1/students/login",
    status_code=status.HTTP_200_OK,
    tags=["Students"],
)
async def student_login(student: StudentLoginSchema = Body(default=None)):
    """Login user"""
    if check_student(student):
        return signJWT(student.email)
    else:
        raise HTTPException(status_code=401, detail="Invalid login details!")


@app.post("/courses/signup", tags=["Courses"])
def signup_to_course():
    pass
