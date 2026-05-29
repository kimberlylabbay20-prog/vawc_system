from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import shutil
import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt as _bcrypt

import models, schemas, crud
import logging
from database import engine, SessionLocal, Base
from email_utils import send_officer_registration_email

logger = logging.getLogger(__name__)

# ---------- Auth Setup ----------
SECRET_KEY = "vawc-system-secret-key-change-in-production"
ADMIN_SECRET_KEY = os.environ.get("ADMIN_SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 1
security = HTTPBearer(auto_error=False)

# ---------- Account Lockout ----------
LOCKOUT_THRESHOLD = 5
LOCKOUT_DURATION_MINUTES = 15
failed_login_attempts: dict = {}

# ---------- App Initialization ----------
app = FastAPI(
    title="Barangay VAWC Case Management System",
    description="Professional case management system for Barangay VAWC. Supports case reporting, triage, assignment, tracking, referrals, and analytics.",
    version="2.0.0",
    contact={"name": "Barangay VAWC Admin", "email": "admin@barangayvawc.gov.ph"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=[
        {"name": "Authentication", "description": "User registration, login, and profile management"},
        {"name": "Case Management", "description": "Full CRUD for cases: create, read, update, delete, assign, note, resolve, archive, refer"},
        {"name": "Dashboard & Analytics", "description": "Dashboard statistics, monthly trends, priority/status breakdowns, officer workload"},
        {"name": "Notifications", "description": "System notifications for case updates, urgent alerts, and reminders"},
        {"name": "User Management", "description": "Officer/Admin user administration: list, update, deactivate"},
        {"name": "Evidence", "description": "Upload, list, and delete evidence files attached to cases"},
        {"name": "Referrals", "description": "Refer cases to external agencies (PNP, DSWD, Hospital) and track referral status"},
        {"name": "System", "description": "Health check and system status endpoints"},
    ],
)

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Base tables created/verified")
        from database import sync_schema
        sync_schema()
        logger.info("Database schema sync completed successfully")

        # Create Case records for existing reports that don't have one
        try:
            from sqlalchemy import inspect as sa_inspect
            inspector = sa_inspect(engine)
            if "cases" in inspector.get_table_names():
                migration_db = SessionLocal()
                try:
                    subq = migration_db.query(models.Case.report_id).subquery()
                    orphans = migration_db.query(models.Report).filter(
                        ~models.Report.id.in_(subq)
                    ).all()
                    if orphans:
                        for report in orphans:
                            case = models.Case(report_id=report.id, status=report.status or "Submitted")
                            migration_db.add(case)
                        migration_db.commit()
                        logger.info("Created %d missing Case records for existing reports", len(orphans))
                except Exception as mig_e:
                    logger.warning("Case migration issue: %s", mig_e)
                finally:
                    migration_db.close()
        except Exception as e:
            logger.warning("Case migration check skipped: %s", e)

    except Exception as e:
        logger.error("Database startup failed: %s", e)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Static Files ----------
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------- Templates ----------
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# ---------- Database Dependency ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# =====================================================================
# GLOBAL EXCEPTION HANDLERS
# =====================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500, "type": type(exc).__name__},
    )

# =====================================================================
# AUTH HELPERS
# =====================================================================

def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = crud.get_user(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

def require_role(*roles: str):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Unauthorized")
        return current_user
    return role_checker

# =====================================================================
# EXISTING ENDPOINTS (KEEP INTACT - ADDED TAGS + RESPONSE MODELS)
# =====================================================================

EXISTING_TAG = "Public Forms"

@app.post("/submit_report", tags=[EXISTING_TAG])
def submit_report(
    victim_name: str = Form(..., min_length=1, max_length=200),
    contact_number: str = Form(..., min_length=7, max_length=50),
    incident_type: str = Form(..., min_length=1, max_length=200),
    description: str = Form(..., min_length=10, max_length=5000),
    location: str = Form(..., min_length=1, max_length=300),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    file_path = None
    if file:
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    new_report = crud.create_report_with_file(
        db, victim_name, contact_number, incident_type, description, location, file_path
    )

    priority = crud.triage_case(description, incident_type, file is not None)
    case_id = crud.generate_case_id(db)

    new_report.priority = priority
    new_report.case_id = case_id
    db.commit()
    db.refresh(new_report)

    new_case = models.Case(report_id=new_report.id, status="Submitted")
    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    crud.log_activity(db, new_case.id, "Case submitted", None)
    crud.create_notification(db, new_report.id, f"New {priority} priority case: {case_id}", "admin")

    if priority == "HIGH":
        crud.create_notification(db, new_report.id, f"URGENT case {case_id} requires immediate attention", "all")
        crud.create_notification(db, new_report.id, f"HIGH PRIORITY case {case_id} - notify PNP/DSWD", "pnp")
        crud.create_notification(db, new_report.id, f"HIGH PRIORITY case {case_id} - notify PNP/DSWD", "dswd")

    return {"message": "Report submitted", "case_id": case_id, "priority": priority, "file": file_path}

@app.get("/view_reports", tags=[EXISTING_TAG])
def view_reports(db: Session = Depends(get_db)):
    return crud.get_reports(db)

@app.get("/", response_class=HTMLResponse, tags=[EXISTING_TAG], include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse, tags=[EXISTING_TAG], include_in_schema=False)
def admin_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/report", response_class=HTMLResponse, tags=[EXISTING_TAG], include_in_schema=False)
def report_form(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})

# =====================================================================
# AUTH ENDPOINTS
# =====================================================================

AUTH_TAG = "Authentication"

@app.post("/api/register", tags=[AUTH_TAG])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        if crud.get_user_by_username(db, user.username):
            raise HTTPException(status_code=400, detail="Username already taken")
        if crud.get_user_by_email(db, user.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        if user.role == "admin":
            if not user.admin_secret or user.admin_secret != ADMIN_SECRET_KEY:
                raise HTTPException(status_code=403, detail="Invalid admin secret key")
        elif user.role not in ("admin", "officer", "user"):
            user.role = "user"

        password_hash = hash_password(user.password)
        db_user = crud.create_user(db, user, password_hash)

        if user.role == "officer":
            db_user.account_status = "pending"
            db_user.is_active = False
            db.commit()
            db.refresh(db_user)
            from database import SessionLocal
            notif_db = SessionLocal()
            try:
                crud.create_notification(notif_db, None, "New officer registration request", "admin")
            finally:
                notif_db.close()
            send_officer_registration_email(
                full_name=user.full_name,
                username=user.username,
                email=user.email,
                barangay=user.barangay
            )

        token = create_access_token({"user_id": db_user.id, "role": db_user.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
                "full_name": db_user.full_name,
                "role": db_user.role,
                "account_status": db_user.account_status,
                "barangay": db_user.barangay,
                "contact_number": db_user.contact_number,
                "is_active": db_user.is_active,
                "created_at": db_user.created_at.isoformat() if db_user.created_at else None,
            }
        }
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Registration failed. Please check your input.")

@app.post("/api/login", tags=[AUTH_TAG])
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    try:
        now = datetime.utcnow()
        record = failed_login_attempts.get(credentials.username)

        if record and record["locked_until"] and now < record["locked_until"]:
            logger.warning("Locked account login attempt: %s", credentials.username)
            raise HTTPException(status_code=423, detail="Account temporarily locked")

        user = crud.get_user_by_username(db, credentials.username)
        if not user or not verify_password(credentials.password, user.password_hash):
            attempt = failed_login_attempts.setdefault(credentials.username, {"count": 0, "locked_until": None})
            attempt["count"] += 1
            logger.warning("Failed login for %s (attempt %d/%d)", credentials.username, attempt["count"], LOCKOUT_THRESHOLD)
            if attempt["count"] >= LOCKOUT_THRESHOLD:
                attempt["locked_until"] = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                attempt["count"] = 0
                logger.warning("Account locked: %s for %d minutes", credentials.username, LOCKOUT_DURATION_MINUTES)
                raise HTTPException(status_code=423, detail="Account temporarily locked")
            raise HTTPException(status_code=401, detail="Invalid username or password")

        failed_login_attempts.pop(credentials.username, None)

        status = (user.account_status or "approved").lower()
        if status == "pending":
            raise HTTPException(status_code=403, detail="Account awaiting admin approval")
        if status == "rejected":
            raise HTTPException(status_code=403, detail="Account request rejected")
        if status == "archived":
            raise HTTPException(status_code=403, detail="Account has been archived")

        token = create_access_token({"user_id": user.id, "role": user.role})
        logger.info("Successful login: %s (role=%s)", user.username, user.role)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "account_status": user.account_status,
                "barangay": user.barangay,
                "contact_number": user.contact_number,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
        }
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=401, detail="Login failed. Please try again.")

@app.get("/api/me", tags=[AUTH_TAG])
def get_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "account_status": current_user.account_status,
        "barangay": current_user.barangay,
        "contact_number": current_user.contact_number,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }

# =====================================================================
# CASE MANAGEMENT ENDPOINTS
# =====================================================================

CASES_TAG = "Case Management"

@app.get("/api/cases", tags=[CASES_TAG])
def list_cases(
    status: str = None,
    priority: str = None,
    search: str = None,
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    cases = crud.get_all_cases_full(db)

    if status:
        cases = [c for c in cases if c.status and c.status.lower() == status.lower()]

    if priority:
        cases = [c for c in cases if c.priority and c.priority.upper() == priority.upper()]

    if search:
        search_lower = search.lower()
        cases = [c for c in cases if
            (c.case_id and search_lower in c.case_id.lower()) or
            (c.victim_name and search_lower in c.victim_name.lower()) or
            (c.incident_type and search_lower in c.incident_type.lower())]

    result = []
    for c in cases:
        officer_name = None
        if c.assigned_to:
            user = crud.get_user(db, c.assigned_to)
            if user:
                officer_name = user.full_name
        result.append({
            "id": c.id,
            "case_id": c.case_id,
            "victim_name": c.victim_name,
            "incident_type": c.incident_type,
            "status": c.status,
            "priority": c.priority,
            "assigned_to": c.assigned_to,
            "assigned_to_name": officer_name,
            "date_reported": c.date_reported.isoformat() if c.date_reported else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None
        })
    return result

@app.get("/api/cases/{case_id}", tags=[CASES_TAG])
def get_case_detail(case_id: int, current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    officer_name = None
    if case.assigned_to:
        user = crud.get_user(db, case.assigned_to)
        if user:
            officer_name = user.full_name
    activities = crud.get_case_activities(db, case_id)
    referrals = crud.get_case_referrals(db, case_id)
    return {
        "case": {
            "id": case.id,
            "case_id": case.case_id,
            "victim_name": case.victim_name,
            "contact_number": case.contact_number,
            "incident_type": case.incident_type,
            "description": case.description,
            "location": case.location,
            "status": case.status,
            "priority": case.priority,
            "assigned_to": case.assigned_to,
            "assigned_to_name": officer_name,
            "file_path": case.file_path,
            "case_notes": case.case_notes,
            "resolution_notes": case.resolution_notes,
            "date_reported": case.date_reported.isoformat() if case.date_reported else None,
            "updated_at": case.updated_at.isoformat() if case.updated_at else None
        },
        "activities": [
            {
                "id": a.id,
                "action": a.action,
                "notes": a.notes,
                "created_at": a.created_at.isoformat() if a.created_at else None
            } for a in activities
        ],
        "referrals": [
            {
                "id": r.id,
                "referred_to": r.referred_to,
                "reason": r.reason,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None
            } for r in referrals
        ]
    }

@app.put("/api/cases/{case_id}", tags=[CASES_TAG])
def update_case(
    case_id: int,
    update: schemas.ReportUpdate,
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    case = crud.update_case(db, case_id, update)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    crud.log_activity(db, case_id, f"Status updated to {case.status}", current_user.id)
    return case

@app.delete("/api/cases/{case_id}", tags=[CASES_TAG])
def delete_case(
    case_id: int,
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete(case)
    db.commit()
    return {"message": "Case deleted", "case_id": case_id}

@app.post("/api/cases/{case_id}/assign", tags=[CASES_TAG])
def assign_case(
    case_id: int,
    officer_id: int = Form(..., ge=1),
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    case = crud.assign_case(db, case_id, officer_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    officer = crud.get_user(db, officer_id)
    crud.create_notification(db, case_id, f"Case assigned to {officer.full_name if officer else 'officer'}", "officer")
    crud.create_notification(db, case_id, f"Case #{case_id} assigned", "admin")
    return case

@app.post("/api/cases/{case_id}/note", tags=[CASES_TAG])
def add_note(
    case_id: int,
    notes: str = Form(..., min_length=1, max_length=5000),
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    case = crud.add_case_note(db, case_id, notes, current_user.id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.post("/api/cases/{case_id}/resolve", tags=[CASES_TAG])
def resolve_case(
    case_id: int,
    resolution_notes: str = Form(..., min_length=10, max_length=5000),
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    case = crud.resolve_case(db, case_id, resolution_notes, current_user.id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    crud.create_notification(db, case_id, f"Case resolved: {case.case_id}", "admin")
    return case

@app.post("/api/cases/{case_id}/archive", tags=[CASES_TAG])
def archive_case(
    case_id: int,
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    case = crud.archive_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.post("/api/cases/{case_id}/refer", tags=[CASES_TAG])
def refer_case(
    case_id: int,
    referral: schemas.ReferralCreate,
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    ref = crud.create_referral(db, case_id, referral.referred_to, referral.reason)
    return ref

@app.get("/api/cases/{case_id}/activities", tags=[CASES_TAG])
def case_activities(case_id: int, current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return crud.get_case_activities(db, case_id)

@app.get("/api/cases/{case_id}/referrals", tags=[CASES_TAG])
def case_referrals(case_id: int, current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return crud.get_case_referrals(db, case_id)

# =====================================================================
# DASHBOARD / ANALYTICS
# =====================================================================

DASHBOARD_TAG = "Dashboard & Analytics"

@app.get("/api/dashboard/stats", tags=[DASHBOARD_TAG])
def dashboard_stats(current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)

@app.get("/api/dashboard/monthly", tags=[DASHBOARD_TAG])
def monthly_stats(year: int = None, current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    return crud.get_monthly_stats(db, year)

@app.get("/api/dashboard/priority", tags=[DASHBOARD_TAG])
def priority_breakdown(current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    return crud.get_priority_breakdown(db)

@app.get("/api/dashboard/status", tags=[DASHBOARD_TAG])
def status_breakdown(current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    return crud.get_status_breakdown(db)

@app.get("/api/dashboard/workload", tags=[DASHBOARD_TAG])
def officer_workload(current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    return crud.get_officer_workload(db)

@app.get("/api/dashboard/activity", tags=[DASHBOARD_TAG])
def recent_activity(limit: int = 10, current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    activities = crud.get_recent_activities(db, limit)
    result = []
    for a in activities:
        name = None
        if a.performed_by:
            user = crud.get_user(db, a.performed_by)
            if user:
                name = user.full_name
        report_id = a.case_id
        case = db.query(models.Case).filter(models.Case.id == a.case_id).first()
        if case:
            report_id = case.report_id
        result.append({
            "id": a.id,
            "case_id": report_id,
            "action": a.action,
            "performed_by": a.performed_by,
            "performed_by_name": name,
            "notes": a.notes,
            "created_at": a.created_at.isoformat() if a.created_at else None
        })
    return result

# =====================================================================
# EVIDENCE
# =====================================================================

EVIDENCE_TAG = "Evidence"

@app.post("/api/cases/{case_id}/evidence", tags=[EVIDENCE_TAG])
def upload_evidence(
    case_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    filename = file.filename or "unnamed"
    file_path = f"uploads/evidence_{case_id}_{filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else None
    ev = crud.create_evidence(db, case_id, filename, file_path, file_type, current_user.id)
    return ev

@app.get("/api/cases/{case_id}/evidence", tags=[EVIDENCE_TAG])
def list_evidence(case_id: int, current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return crud.get_case_evidence(db, case_id)

@app.delete("/api/evidence/{evidence_id}", tags=[EVIDENCE_TAG])
def delete_evidence(
    evidence_id: int,
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    ev = crud.delete_evidence(db, evidence_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    if os.path.exists(ev.file_path):
        os.remove(ev.file_path)
    return {"message": "Evidence deleted"}


# =====================================================================
# NOTIFICATIONS
# =====================================================================

NOTIF_TAG = "Notifications"

@app.get("/api/notifications", tags=[NOTIF_TAG])
def list_notifications(current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    return crud.get_notifications(db, role=current_user.role)

@app.put("/api/notifications/{notif_id}/read", tags=[NOTIF_TAG])
def mark_read(notif_id: int, current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    notif = crud.mark_notification_read(db, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif

@app.put("/api/notifications/read-all", tags=[NOTIF_TAG])
def mark_all_read(current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    crud.mark_all_notifications_read(db, role=current_user.role)
    return {"message": "All notifications marked as read"}

@app.get("/api/notifications/unread-count", tags=[NOTIF_TAG])
def unread_count(current_user: models.User = Depends(require_role("admin", "officer")), db: Session = Depends(get_db)):
    return {"count": crud.get_unread_notification_count(db, role=current_user.role)}

@app.get("/api/notifications/history", tags=[NOTIF_TAG])
def notification_history(
    offset: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    return crud.get_notification_history(db, role=current_user.role, offset=offset, limit=limit)

@app.put("/api/notifications/{notif_id}/archive", tags=[NOTIF_TAG])
def archive_notification(
    notif_id: int,
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    notif = crud.archive_notification(db, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif

@app.delete("/api/notifications/{notif_id}", tags=[NOTIF_TAG])
def delete_notification(
    notif_id: int,
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    notif = crud.delete_notification(db, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}

# =====================================================================
# USERS
# =====================================================================

USERS_TAG = "User Management"

@app.get("/api/users", tags=[USERS_TAG])
def list_users(current_user: models.User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return crud.get_users(db)

@app.put("/api/users/{user_id}", tags=[USERS_TAG])
def update_user(
    user_id: int,
    update: schemas.UserUpdate,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_dict = update.model_dump(exclude_unset=True)
    if "email" in update_dict and update_dict["email"]:
        existing = crud.get_user_by_email(db, update_dict["email"])
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email already in use")
    for key, value in update_dict.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

@app.delete("/api/users/{user_id}", tags=[USERS_TAG])
def delete_user(
    user_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": "User deactivated", "user_id": user_id}

@app.post("/api/users/{user_id}/approve", tags=[USERS_TAG])
def approve_user(
    user_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.account_status = "approved"
    user.is_active = True
    db.commit()
    db.refresh(user)
    logger.info("Officer approved: %s", user.username)
    return {"message": "Officer approved", "user_id": user_id, "username": user.username}

@app.post("/api/users/{user_id}/reject", tags=[USERS_TAG])
def reject_user(
    user_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.account_status = "rejected"
    user.is_active = False
    db.commit()
    db.refresh(user)
    logger.info("Officer rejected: %s", user.username)
    return {"message": "Officer rejected", "user_id": user_id, "username": user.username}

@app.post("/api/users/{user_id}/archive", tags=[USERS_TAG])
def archive_user(
    user_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot archive yourself")
    user.account_status = "archived"
    user.is_active = False
    db.commit()
    db.refresh(user)
    logger.info("Officer archived: %s", user.username)
    return {"message": "Officer archived", "user_id": user_id, "username": user.username}

@app.delete("/api/users/{user_id}/delete", tags=[USERS_TAG])
def hard_delete_user(
    user_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    logger.info("Officer deleted: %s (id=%d)", user.username, user_id)
    return {"message": "Officer deleted", "user_id": user_id}

# =====================================================================
# REFERRALS
# =====================================================================

REFERRAL_TAG = "Referrals"

@app.put("/api/referrals/{referral_id}/status", tags=[REFERRAL_TAG])
def update_referral_status(
    referral_id: int,
    update: schemas.ReferralUpdate,
    current_user: models.User = Depends(require_role("admin", "officer")),
    db: Session = Depends(get_db)
):
    referral = db.query(models.Referral).filter(models.Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    referral.status = update.status
    db.commit()
    db.refresh(referral)
    crud.log_activity(db, referral.case_id, f"Referral status updated to {update.status}", current_user.id)
    return referral

# =====================================================================
# HEALTH CHECK
# =====================================================================

HEALTH_TAG = "System"

@app.get("/api/health", tags=[HEALTH_TAG])
def health_check():
    db_status = "ok"
    db_error = None
    from sqlalchemy import text
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = "error"
        db_error = f"{type(e).__name__}: {str(e)[:200]}"
    return {
        "status": "ok",
        "database": db_status,
        "database_error": db_error,
        "timestamp": datetime.utcnow().isoformat()
    }
