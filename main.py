from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models, schemas, crud
from database import engine, SessionLocal, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VAWC Reporting System",
    description="Submit reports under VAWC"
)

# Templates (IMPORTANT)
templates = Jinja2Templates(directory="templates")

# CORS (para walang error sa frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ HOMEPAGE (ITO ANG MAGPAPALABAS NG UI)
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})

# ✅ SUBMIT REPORT
@app.post("/submit_report")
def submit_report(report: schemas.ReportCreate, db: Session = Depends(get_db)):
    new_report = crud.create_report(db, report)
    return {
        "message": "Report submitted successfully",
        "id": new_report.id
    }

# ✅ VIEW REPORTS
@app.get("/view_reports")
def view_reports(db: Session = Depends(get_db)):
    return crud.get_reports(db)