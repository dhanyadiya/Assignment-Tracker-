from fastapi import FastAPI, Request, Form, Depends, status, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import shutil, os
from datetime import datetime
from database import SessionLocal, engine
import models
from models import Assignment, Submission, Student, Teacher

# -------------------- INITIAL SETUP --------------------
os.makedirs("uploads/assignments", exist_ok=True)
os.makedirs("uploads/submissions", exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.get("/assignments/")
def list_assignments(db: Session = Depends(get_db)):
    return db.query(Assignment).all()
# -------------------- HOME --------------------
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------- STUDENT SIGNUP & LOGIN --------------------
@app.get("/signup/student", response_class=HTMLResponse)
def get_signup_form(request: Request):
    return templates.TemplateResponse("student_signup.html", {"request": request})

@app.post("/signup/student")
def signup_student(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    roll_number: str = Form(...),
    year: int = Form(...),
    class_name: str = Form(...),
    db: Session = Depends(get_db)
):
    student = Student(
        name=name,
        email=email,
        password=password,
        roll_number=roll_number,
        year=year,
        class_name=class_name
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

@app.get("/login/student", response_class=HTMLResponse)
def student_login_form(request: Request):
    return templates.TemplateResponse("student_login.html", {"request": request})

@app.post("/login/student")
def student_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.email == email).first()
    if not student or student.password != password:
        return templates.TemplateResponse("student_login.html", {
            "request": request,
            "error": "Invalid email or password"
        })
    return RedirectResponse(f"/dashboard/student/{student.id}", status_code=status.HTTP_302_FOUND)

# -------------------- STUDENT DASHBOARD --------------------
@app.get("/dashboard/student/{student_id}", response_class=HTMLResponse)
def student_dashboard(student_id: int, request: Request, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    assignments = db.query(Assignment).filter(Assignment.class_name == student.class_name).all()
    return templates.TemplateResponse("student_dashboard.html", {
        "request": request,
        "student": student,
        "assignments": assignments
    })


# ------------------- Show Submission Form ---------------------
@app.get("/student/submit-assignment/{assignment_id}/{student_id}", response_class=HTMLResponse)
def get_submit_form(assignment_id: int, student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not student or not assignment:
        return HTMLResponse("<h3>Student or Assignment not found.</h3>", status_code=404)

    if student.class_name != assignment.class_name:
        return HTMLResponse("<h3>Assignment not assigned to your class.</h3>", status_code=403)

    return f"""
        <h2>Submit Assignment: {assignment.title}</h2>
        <form action="/student/submit-assignment/{assignment_id}/{student_id}" method="post" enctype="multipart/form-data">
            <input type="file" name="submission_file" required><br><br>
            <button type="submit">Submit</button>
        </form>
    """


# ------------------- Handle Assignment Submission ---------------------
@app.post("/student/submit-assignment/{assignment_id}/{student_id}")
def submit_assignment(
    assignment_id: int,
    student_id: int,
    submission_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not student or not assignment:
        raise HTTPException(status_code=404, detail="Student or Assignment not found")

    if student.class_name != assignment.class_name:
        raise HTTPException(status_code=403, detail="Student class does not match assignment class")

    os.makedirs("uploads/submissions", exist_ok=True)
    file_path = f"uploads/submissions/{student.id}_{assignment.id}_{submission_file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(submission_file.file, buffer)

    submission = Submission(
        assignment_id=assignment.id,
        student_id=student.id,
        file_path=file_path,
        submitted_at=datetime.utcnow()
    )

    db.add(submission)
    db.commit()

    return HTMLResponse(f"""
        <h3>Assignment submitted successfully!</h3>
        <p><strong>Assignment:</strong> {assignment.title}</p>
        <p><strong>Subject:</strong> {assignment.subject}</p>
        <p><strong>Class:</strong> {assignment.class_name}</p>
        <p><strong>File:</strong> {submission_file.filename}</p>
    """, status_code=200)
# -------------------- STUDENT PROFILE --------------------
@app.get("/student/profile/{student_id}", response_class=HTMLResponse)
def view_student_profile(student_id: int, request: Request, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return templates.TemplateResponse("student_profile.html", {
        "request": request,
        "student": student
    })

@app.post("/student/profile/{student_id}")
def update_student_profile(
    student_id: int,
    name: str = Form(...),
    email: str = Form(...),
    roll_number: str = Form(...),
    year: int = Form(...),
    class_name: str = Form(...),
    password: str = Form(None),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.name = name
    student.email = email
    student.roll_number = roll_number
    student.year = year
    student.class_name = class_name
    if password:
        student.password = password

    db.commit()
    return RedirectResponse(f"/student/profile/{student.id}", status_code=status.HTTP_302_FOUND)

# -------------------- TEACHER SIGNUP & LOGIN --------------------
@app.get("/signup/teacher", response_class=HTMLResponse)
def get_teacher_signup_form(request: Request):
    return templates.TemplateResponse("teacher_signup.html", {"request": request})

@app.post("/signup/teacher")
def signup_teacher(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    emp_id: str = Form(...),
    db: Session = Depends(get_db)
):
    teacher = Teacher(
        name=name,
        email=email,
        password=password,
        emp_id=emp_id
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

@app.get("/login/teacher", response_class=HTMLResponse)
def teacher_login_form(request: Request):
    return templates.TemplateResponse("teacher_login.html", {"request": request})

@app.post("/login/teacher")
def teacher_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).filter(Teacher.email == email).first()
    if not teacher or teacher.password != password:
        return templates.TemplateResponse("teacher_login.html", {
            "request": request,
            "error": "Invalid email or password"
        })
    return RedirectResponse(f"/dashboard/teacher/{teacher.id}", status_code=status.HTTP_302_FOUND)

# -------------------- TEACHER DASHBOARD --------------------
@app.get("/dashboard/teacher/{teacher_id}", response_class=HTMLResponse)
def teacher_dashboard(teacher_id: int, request: Request, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    assignments = db.query(Assignment).filter(Assignment.teacher_id == teacher.id).all()

    submissions = (
        db.query(Submission, Student)
        .join(Student, Submission.student_id == Student.id)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .filter(Assignment.teacher_id == teacher.id)
        .all()
    )

    submission_data = []
    for submission, student in submissions:
        submission_data.append({
            "student_name": student.name,
            "date": submission.submitted_at.strftime("%Y-%m-%d %H:%M") if submission.submitted_at else "N/A",
            "file_url": f"/{submission.file_path}" if submission.file_path else None
        })

    return templates.TemplateResponse("teacher_dashboard.html", {
        "request": request,
        "teacher": teacher,
        "assignments": assignments,
        "submissions": submission_data
    })

@app.post("/teacher/create-assignment")
async def create_assignment(
    subject: str = Form(...),
    class_name: str = Form(...),
    title: str = Form(...),
    assignment_type: str = Form(...),
    teacher_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_path = f"uploads/assignments/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    assignment = Assignment(
        subject=subject,
        class_name=class_name,
        title=title,
        assignment_type=assignment_type,
        file_path=file_path,
        teacher_id=teacher_id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return RedirectResponse(url=f"/dashboard/teacher/{teacher_id}", status_code=303)


# -------------------- TEACHER PROFILE --------------------
@app.get("/teacher/profile/{teacher_id}", response_class=HTMLResponse)
def view_teacher_profile(teacher_id: int, request: Request, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return templates.TemplateResponse("teacher_profile.html", {
        "request": request,
        "teacher": teacher
    })

@app.post("/teacher/profile/{teacher_id}")
def update_teacher_profile(
    teacher_id: int,
    name: str = Form(...),
    email: str = Form(...),
    emp_id: str = Form(...),
    password: str = Form(None),
    db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher.name = name
    teacher.email = email
    teacher.emp_id = emp_id
    if password:
        teacher.password = password

    db.commit()
    return RedirectResponse(f"/teacher/profile/{teacher.id}", status_code=status.HTTP_302_FOUND)
