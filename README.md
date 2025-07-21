# EdTech Assignment Tracker

## Overview

TDesign and implement a simplified assignment tracking system for an EdTech platform that allows teachers to post assignments and students to submit them.
---


## Feature
- User Authentication (Register/Login) for Teachers and Students
- User Profile Management
- Assignment Creation with Title, Description, and Deadlines
- Student Assignment Viewing & File Submission
- Teacher Dashboard to View Submissions
- Secure Data Handling

---

## Tech Stack

### Frontend:
- **HTML**
- **CSS**
- **JavaScript**

### Backend:
- **FastAPI (Python)**

### Database:
- **SQLite**



## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/dhanyadiya/Assignment-Tracker-.git
cd cd assignment_tracker 
### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate(Windows)
source venv/bin/activate(macOS/Linux)
### 3. install dependency
pip install fastapi uvicorn sqlalchemy jinja2 aiofiles python-multipart
### 4. Start the FastAPI Server
uvicorn main:app --reload

