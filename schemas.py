from pydantic import BaseModel
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    email: str
    password: str
    roll_number: Optional[str]
    year: Optional[int]
    class_name: str
    
class TeacherCreate(BaseModel):
    name: str
    email: str
    password: str
    emp_id: str


class AssignmentCreate(BaseModel):
    subject: str
    class_name: str
    title: str
    assignment_type: str  # e.g., "file"

class Submission(BaseModel):
    assignment_id: int
    student_id: int
    file_path: str