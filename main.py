import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Security
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from app.db import db
from app.jwt_auth import Auth
from app.models import Course
from app.models import CourseSignUp
from app.models import Student
from app.schemas import CourseSchema
from app.schemas import CourseSignUpSchema
from app.schemas import CourseUpdateSchema
from app.schemas import StudentListSchema
from app.schemas import StudentLoginSchema
from app.schemas import StudentSchema


security = HTTPBearer()
auth_handler = Auth()

description = """
Course API helps you do awesome stuff (someday, maybe). \n
It uses PostgreSQL and SQLAlchemy + Alembic under the hood \n
with JWT for authentication. Passwords are stored encrypted.

## Courses

You can search, add, modify and delete courses.

## Students

You can search, add and delete student's accounts.

## Course Signup

You can signup the student the course.

"""


tags_metadata = [
    {"name": "Courses", "description": "Endpoints to work with courses"},
    {"name": "Students", "description": "Endpoints to work with students"},
]

app = FastAPI(
    openapi_tags=tags_metadata,
    title="Course subscription on FastAPI",
    description=description,
    version="0.1.0",
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


# route handlers
# Courses
@app.get(
    "/api/v1/courses",
    response_model=list[CourseSchema],
    status_code=status.HTTP_200_OK,
    tags=["Courses"],
)
async def get_all_courses():
    """Get a list of all courses"""
    courses = db.query(Course).all()
    return courses


@app.get(
    "/api/v1/courses/{id}",
    response_model=CourseSchema,
    status_code=status.HTTP_200_OK,
    tags=["Courses"],
)
async def get_single_course(id: int):
    """Find the course by ID"""
    course = db.query(Course).filter(Course.course_id == id).first()

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return course


@app.post(
    "/api/v1/courses",
    status_code=status.HTTP_201_CREATED,
    response_model=CourseSchema,
    tags=["Courses"],
)
async def add_course(
    course: CourseSchema,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """Add a new course"""
    token = credentials.credentials
    if not auth_handler.decode_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must authorize to add the course",
        )
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


@app.put(
    "/api/v1/courses/{course_id}",
    response_model=CourseUpdateSchema,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Courses"],
)
async def update_the_course(
    course_id: int,
    course: CourseUpdateSchema,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """Update the course by ID"""
    token = credentials.credentials
    if not auth_handler.decode_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must authorize to change the course",
        )
    updated_course = (
        db.query(Course).filter(Course.course_id == course_id).first()
    )
    if updated_course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    updated_course.title = course.title
    updated_course.description = course.description
    db.commit()

    return updated_course


@app.delete(
    "/api/v1/courses/{course_id}",
    response_model=CourseUpdateSchema,
    status_code=200,
    tags=["Courses"],
)
async def delete_the_course(
    course_id: int,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """Delete the course by ID"""
    token = credentials.credentials
    if not auth_handler.decode_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must authorize to delete the course",
        )
    course_to_delete = (
        db.query(Course).filter(Course.course_id == course_id).first()
    )
    if course_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    db.delete(course_to_delete)
    db.commit()
    return course_to_delete


@app.get(
    "/api/v1/students",
    response_model=list[StudentListSchema],
    status_code=status.HTTP_200_OK,
    tags=["Students"],
)
async def get_all_students():
    """Show a list of all students"""
    students = db.query(Student).all()
    return students


@app.post(
    "/api/v1/students/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=StudentSchema,
    tags=["Students"],
)
async def signup_student(student: StudentSchema):
    """Create a new student's account"""
    db_student = (
        db.query(Student).filter(Student.email == student.email).first()
    )

    if db_student is not None:
        raise HTTPException(
            status_code=400, detail="User with the same email already exists"
        )

    hashed_password = auth_handler.encode_password(student.password)
    new_student = Student(
        fullname=student.fullname,
        email=student.email,
        password=hashed_password,
    )

    db.add(new_student)
    db.commit()
    return new_student


@app.post(
    "/api/v1/students/login",
    status_code=status.HTTP_200_OK,
    tags=["Students"],
)
async def student_login(student: StudentLoginSchema):
    """Login student into the account"""
    student_db = (
        db.query(Student).filter(Student.email == student.email).first()
    )
    if student_db is None:
        raise HTTPException(status_code=401, detail="Invalid login details!")
    if not auth_handler.verify_password(student.password, student_db.password):
        raise HTTPException(status_code=401, detail="Invalid login details!")
    access_token = auth_handler.encode_token(student.email)
    refresh_token = auth_handler.encode_refresh_token(student.email)

    return {"access_token": access_token, "refresh_token": refresh_token}


@app.delete(
    "/api/v1/studets/{student_id}",
    response_model=StudentSchema,
    status_code=status.HTTP_200_OK,
    tags=["Students"],
)
async def delete_student_account(
    student_id: int,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """Delete student's account"""
    token = credentials.credentials
    if auth_handler.decode_token(token):
        account_to_delete = (
            db.query(Student).filter(Student.student_id == student_id).first()
        )
        if account_to_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student account not found",
            )
        db.delete(account_to_delete)
        db.commit()
        return account_to_delete


@app.post(
    "/api/v1/courses/signup",
    response_model=CourseSignUpSchema,
    tags=["Courses"],
)
def signup_to_the_course(
    payload: CourseSignUpSchema,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """Signup to the course"""
    token = credentials.credentials
    if auth_handler.decode_token(token):
        new_signup = CourseSignUp(
            student_id=payload.student_id, course_id=payload.course_id
        )
        check_student_id = (
            db.query(Student)
            .filter(Student.student_id == payload.student_id)
            .first()
        )
        if check_student_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )
        check_course_id = (
            db.query(Course)
            .filter(Course.course_id == payload.course_id)
            .first()
        )
        if check_course_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        db_check_double = (
            db.query(CourseSignUp)
            .filter(
                CourseSignUp.student_id == payload.student_id,
                CourseSignUp.course_id == payload.course_id,
            )
            .first()
        )
        if db_check_double is not None:
            raise HTTPException(
                status_code=400,
                detail="You already have been signed up for the course",
            )
        db.add(new_signup)
        db.commit()
        return new_signup


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content="Wrong arguments, please check the example schema",
    )


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
