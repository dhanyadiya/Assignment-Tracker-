from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    roll_number = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    class_name = Column(String, nullable=False)

class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    emp_id = Column(String, unique=True, nullable=False)

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    assignment_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    
    teacher = relationship("Teacher")  
    
class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    file_path = Column(String, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    assignment = relationship("Assignment")
    student = relationship("Student")