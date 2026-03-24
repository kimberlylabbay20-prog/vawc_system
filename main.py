from fastapi import FastAPI, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil
import os

import models, schemas, crud
from database import engine, SessionLocal, Base

# Auto-create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VAWC Reporting System",
    description="Submit reports under VAWC"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📁 gumawa ng uploads folder kung wala pa
if not os.path.exists("uploads"):
    os.makedirs("uploads")


# ✅ UPDATED ENDPOINT (WITH FILE UPLOAD)
@app.post("/submit_report")
def submit_report(
    victim_name: str = Form(...),
    contact_number: str = Form(...),
    incident_type: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    file: UploadFile = File(None),  # optional
    db: Session = Depends(get_db)
):
    file_path = None

    # 📎 save file kung meron
    if file:
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # 🗃 save sa database
    new_report = crud.create_report_with_file(
        db,
        victim_name,
        contact_number,
        incident_type,
        description,
        location,
        file_path
    )

    return {
        "message": "Report submitted",
        "file": file_path
    }


# View reports
@app.get("/view_reports")
def view_reports(db: Session = Depends(get_db)):
    return crud.get_reports(db)