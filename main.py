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
def submit_report(
    victim_name: str,
    contact_number: str,
    incident_type: str,
    description: str,
    location: str,
    file: UploadFile = File(None),   # ✅ optional file
    db: Session = Depends(get_db)
):
    file_path = None

    if file:
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    new_report = crud.create_report(
        db,
        victim_name=victim_name,
        contact_number=contact_number,
        incident_type=incident_type,
        description=description,
        location=location,
        file_path=file_path   # optional
    )

    return {"message": "Report submitted", "file": file_path}

# ✅ VIEW REPORTS
@app.get("/view_reports")
def view_reports(db: Session = Depends(get_db)):
    return crud.get_reports(db)