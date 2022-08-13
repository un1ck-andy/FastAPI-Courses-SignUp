from fastapi import Body
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPBearer
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT
from app.jwt_auth import Auth
from app.model import AuthModel
from app.model import CourseSchema
from app.model import StudentLoginSchema
from app.model import StudentSchema


base = declarative_base()

security = HTTPBearer()
auth_handler = Auth()


class Student(base):
    __tablename__ = "students"
    user_id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        unique=True,
        autoincrement=True,
    )
    fullname = Column(String)
    email = Column(String)
    password = Column(String)


class Course(base):
    __tablename__ = "courses"
    course_id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        unique=True,
        autoincrement=True,
    )
    title = Column(String)
    description = Column(String)


class CourseSignUp(base):
    __tablename__ = "course_sign_up"
    course_sing_up_id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        unique=True,
        autoincrement=True,
    )
    student_id = Column(Integer, ForeignKey("students.user_id"))
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    student = relationship(
        "Student", backref="signup_student", lazy="subquery"
    )
    course = relationship("Course", backref="signup_course", lazy="subquery")


engine = create_engine("sqlite:///fastapi.db", echo=True)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

base.metadata.create_all(engine)

app = FastAPI()


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

# Get courses
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
    tags=["courses"],
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
    tags=["test"],
)
async def fetch_students():
    """Show all students list"""
    students = db.query(Student).all()
    return students


@app.post(
    "/api/v1/students/signup",
    status_code=status.HTTP_201_CREATED,
    tags=["students"],
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

    hashed_password = auth_handler.encode_password(student.password)
    new_student = Student(
        fullname=student.fullname,
        email=student.email,
        password=hashed_password,
    )

    db.add(new_student)
    db.commit()
    return signJWT(student.email)


@app.post(
    "/api/v1/students/login",
    status_code=status.HTTP_200_OK,
    tags=["students"],
)
async def student_login(student: AuthModel):
    """Login student"""
    student_db = (
        db.query(Student).filter(Student.email == student.email).first()
    )
    if student_db is None:
        raise HTTPException(status_code=401, detail="Invalid user details!")
    if not auth_handler.verify_password(student.password, student_db.password):
        raise HTTPException(status_code=401, detail="Invalid login details!")

    access_token = auth_handler.encode_token(student_db.email)
    refresh_token = auth_handler.encode_refresh_token(student_db.email)
    return {"access_token": access_token, "refresh_token": refresh_token}
