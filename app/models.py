from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from app.db import engine

base = declarative_base()


class Student(base):
    __tablename__ = "students"
    student_id = Column(
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
    student_id = Column(Integer, ForeignKey("students.student_id"))
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    student = relationship(
        "Student", backref="signup_student", lazy="subquery"
    )
    course = relationship("Course", backref="signup_course", lazy="subquery")


def database_init():
    base.metadata.create_all(engine)
