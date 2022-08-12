import uvicorn
from fastapi import FastAPI, Body, Depends

from app.model import CourseSchema, StudentSchema, StudentLoginSchema, ApplicationsListChema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT


import sqlite3

# courses = [
#     {
#         "id": 1,
#         "title": "First course",
#         "description": "Interesting course",
#         "student_id": ""
#     },
#     {
#         "id": 2,
#         "title": "Second course",
#         "description": "Not so boring as the next one",
#         "student_id": ""
#     },
#     {
#         "id": 3,
#         "title": "Third course",
#         "description": "Don't listen to all, this course is awesome",
#         "student_id": ""
#     },
# ]

# students = [
#     {
#         "id": 1,
#         "fullname": "Thomas Anderson",
#         "email": "neo@matrix.has.you",
#         "password": "weakpassword"
#     }
# ]

# course_applications = []

app = FastAPI()



def check_student(data: StudentLoginSchema):
    for student in students:
        if student.email == data.email and student.password == data.password:
            return True
    return False


# route handlers

# testing
@app.get("/", tags=["test"])
def greet():
    return {"hello": "world!"}


# Get courses
@app.get("/courses", tags=["courses"])
def get_courses():
    return { "data": courses }


@app.get("/courses/{id}", tags=["courses"])
def get_single_course(id: int):
    if id > len(courses):
        return {
            "error": "No such course with the supplied ID."
        }

    for course in courses:
        if course["id"] == id:
            return {
                "data": course
            }


@app.post("/courses", dependencies=[Depends(JWTBearer())], tags=["courses"])
def add_course(course: CourseSchema):
    course.id = len(courses) + 1
    for c in courses:
        if c["title"] == course.title:
            return {
                "data": f"Error: course named '{course.title}' already exists."
            }
    courses.append(course.dict())
    return {
        "data": course.title + " added."
    }


@app.post("/students/signup", tags=["students"])
def signup_student(student: StudentSchema = Body(...)):
    students.append(student) # replace with db call, making sure to hash the password first
    return signJWT(student.email)


@app.post("/students/login", tags=["students"])
def student_login(student: StudentLoginSchema = Body(...)):
    if check_student(student):
        return signJWT(student.email)
    return {
        "error": "Wrong login details!"
    }

@app.post("/courses/signup", tags=["courses"])
def signup_to_course(list: ApplicationsListChema):
    for course in courses:
        if course["id"] == list.course_id:
            course["student_id"] += "," +str(list.student_id)
            return {
                "data": f"{list.student_id} was signed to the course {course['title']}"
            }
  


# id student_id course_id
