from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, SessionLocal, Base

# Auto-create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VAWC Reporting System",
    description="API for submitting and viewing VAWC reports"
)

# ✅ CORS FIX (IMPORTANT)
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

# ✅ FIXED: JSON instead of Form
@app.post("/submit_report")
def submit_report(report: schemas.ReportCreate, db: Session = Depends(get_db)):
    new_report = crud.create_report(db, report)
    return {"message": "Report submitted", "id": new_report.id}

# View reports
@app.get("/view_reports")
def view_reports(db: Session = Depends(get_db)):
    return crud.get_reports(db)