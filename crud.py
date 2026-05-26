from sqlalchemy.orm import Session
from sqlalchemy import func, extract
import models, schemas
from datetime import datetime

# ========== EXISTING CRUD (KEEP INTACT) ==========

def create_report(db: Session, report: schemas.ReportCreate):
    db_report = models.Report(**report.model_dump())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_reports(db: Session):
    return db.query(models.Report).all()

def create_report_with_file(db, victim_name, contact_number, incident_type, description, location, file_path):
    new_report = models.Report(
        victim_name=victim_name,
        contact_number=contact_number,
        incident_type=incident_type,
        description=description,
        location=location,
        file_path=file_path
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

# ========== AUTO TRIAGE ==========

URGENT_KEYWORDS = [
    "emergency", "urgent", "immediate", "life-threatening", "life threatening",
    "hospital", "bleeding", "unconscious", "danger", "weapon", "knife", "gun",
    "severe", "critical", "attack", "strangling", "suffocation", "stab",
    "shoot", "pointed", "held at gunpoint", "armed", "blood", "fracture",
    "broken bone", "ambulance", "er", "emergency room", "panic"
]

MEDIUM_KEYWORDS = [
    "threat", "harassment", "stalking", "multiple", "repeated", "ongoing",
    "physical", "hit", "punch", "slap", "kick", "injury", "bruise", "wound",
    "force", "grabbed", "pushed", "shoved", "choked", "restrained",
    "verbal abuse", "intimidation", "coercion", "manipulation"
]

def triage_case(description: str, incident_type: str, has_evidence: bool = False) -> str:
    desc_lower = description.lower()
    type_lower = incident_type.lower()

    for kw in URGENT_KEYWORDS:
        if kw in desc_lower or kw in type_lower:
            return "HIGH"

    if "emergency" in type_lower or "urgent" in type_lower:
        return "HIGH"

    for kw in MEDIUM_KEYWORDS:
        if kw in desc_lower or kw in type_lower:
            if has_evidence:
                return "HIGH"
            return "MEDIUM"

    if has_evidence:
        return "MEDIUM"

    return "LOW"

def generate_case_id(db: Session) -> str:
    year = datetime.now().year
    count = db.query(models.Report).filter(
        extract("year", models.Report.date_reported) == year
    ).count()
    return f"VAWC-{year}-{count + 1:04d}"

# ========== CASE MANAGEMENT ==========

def get_case(db: Session, case_id: int):
    return db.query(models.Report).filter(models.Report.id == case_id).first()

def get_case_by_case_id(db: Session, case_id_str: str):
    return db.query(models.Report).filter(models.Report.case_id == case_id_str).first()

def update_case(db: Session, case_id: int, update_data: schemas.ReportUpdate):
    case = db.query(models.Report).filter(models.Report.id == case_id).first()
    if not case:
        return None
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            setattr(case, key, value)
    case.updated_at = func.now()
    db.commit()
    db.refresh(case)
    return case

def assign_case(db: Session, case_id: int, officer_id: int):
    case = db.query(models.Report).filter(models.Report.id == case_id).first()
    if not case:
        return None
    old_status = case.status
    case.assigned_to = officer_id
    if case.status == "Submitted":
        case.status = "Assigned"
    db.commit()
    db.refresh(case)
    log_activity(db, case_id, f"Assigned to officer #{officer_id}", officer_id)
    return case

def add_case_note(db: Session, case_id: int, notes: str, officer_id: int):
    case = db.query(models.Report).filter(models.Report.id == case_id).first()
    if not case:
        return None
    existing = case.case_notes or ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    case.case_notes = f"{existing}\n[{timestamp}] Officer #{officer_id}: {notes}".strip()
    db.commit()
    db.refresh(case)
    log_activity(db, case_id, "Note added", officer_id, notes)
    return case

def resolve_case(db: Session, case_id: int, resolution_notes: str, officer_id: int):
    case = db.query(models.Report).filter(models.Report.id == case_id).first()
    if not case:
        return None
    case.status = "Resolved"
    case.resolution_notes = resolution_notes
    db.commit()
    db.refresh(case)
    log_activity(db, case_id, "Case resolved", officer_id, resolution_notes)
    return case

def archive_case(db: Session, case_id: int):
    case = db.query(models.Report).filter(models.Report.id == case_id).first()
    if not case:
        return None
    case.status = "Archived"
    db.commit()
    db.refresh(case)
    log_activity(db, case_id, "Case archived", None)
    return case

# ========== CASE ACTIVITY ==========

def log_activity(db: Session, case_id: int, action: str, performed_by: int = None, notes: str = None):
    # Ensure the ID exists in cases table
    case = db.query(models.Case).filter(models.Case.id == case_id).first()

    # If not found, try resolving via report_id
    if not case:
        case = db.query(models.Case).filter(models.Case.report_id == case_id).first()

    # Still not found? Skip logging to avoid ForeignKeyViolation
    if not case:
        print(f"WARNING: No matching Case found for case_id={case_id}")
        return

    activity = models.CaseActivity(
        case_id=case.id,
        action=action,
        performed_by=performed_by,
        notes=notes
    )

    db.add(activity)
    db.commit()

def get_case_activities(db: Session, case_id: int):
    # Resolve Report.id → Case.id for lookup
    case = db.query(models.Case).filter(models.Case.report_id == case_id).first()
    actual_case_id = case.id if case else case_id
    return db.query(models.CaseActivity).filter(
        models.CaseActivity.case_id == actual_case_id
    ).order_by(models.CaseActivity.created_at.desc()).all()

# ========== NOTIFICATIONS ==========

def create_notification(db: Session, case_id: int, message: str, recipient_role: str):
    notif = models.Notification(
        case_id=case_id,
        message=message,
        recipient_role=recipient_role
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif

def get_notifications(db: Session, role: str = None, limit: int = 20):
    query = db.query(models.Notification).order_by(models.Notification.created_at.desc())
    if role:
        query = query.filter(models.Notification.recipient_role.in_([role, "all"]))
    return query.limit(limit).all()

def mark_notification_read(db: Session, notif_id: int):
    notif = db.query(models.Notification).filter(models.Notification.id == notif_id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return notif

def get_unread_notification_count(db: Session, role: str = None):
    query = db.query(models.Notification).filter(models.Notification.is_read == False)
    if role:
        query = query.filter(models.Notification.recipient_role.in_([role, "all"]))
    return query.count()

# ========== EVIDENCE ==========

def create_evidence(db: Session, case_id: int, filename: str, file_path: str, file_type: str = None, uploaded_by: int = None):
    ev = models.Evidence(
        case_id=case_id,
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        uploaded_by=uploaded_by
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    log_activity(db, case_id, f"Evidence uploaded: {filename}", uploaded_by)
    return ev

def get_case_evidence(db: Session, case_id: int):
    return db.query(models.Evidence).filter(
        models.Evidence.case_id == case_id
    ).order_by(models.Evidence.uploaded_at.desc()).all()

def delete_evidence(db: Session, evidence_id: int):
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        return None
    db.delete(ev)
    db.commit()
    return ev


# ========== REFERRALS ==========

def create_referral(db: Session, case_id: int, referred_to: str, reason: str):
    referral = models.Referral(
        case_id=case_id,
        referred_to=referred_to,
        reason=reason
    )
    db.add(referral)
    db.commit()
    db.refresh(referral)
    log_activity(db, case_id, f"Referred to {referred_to}", None, reason)
    create_notification(db, case_id, f"Case referred to {referred_to}: {reason}", referred_to.lower())
    return referral

def get_case_referrals(db: Session, case_id: int):
    return db.query(models.Referral).filter(
        models.Referral.case_id == case_id
    ).order_by(models.Referral.created_at.desc()).all()

# ========== USER MANAGEMENT ==========

def create_user(db: Session, user: schemas.UserCreate, password_hash: str):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=password_hash,
        full_name=user.full_name,
        role=user.role,
        barangay=user.barangay,
        contact_number=user.contact_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session):
    return db.query(models.User).order_by(models.User.full_name).all()

# ========== DASHBOARD / ANALYTICS ==========

def get_dashboard_stats(db: Session) -> dict:
    total = db.query(models.Report).count()
    active = db.query(models.Report).filter(
        models.Report.status.in_(["Submitted", "Assigned", "Ongoing", "Monitoring"])
    ).count()
    urgent = db.query(models.Report).filter(models.Report.priority == "HIGH").count()
    resolved = db.query(models.Report).filter(
        models.Report.status.in_(["Resolved", "Archived"])
    ).count()
    pending = db.query(models.Report).filter(models.Report.status == "Submitted").count()
    officers = db.query(models.User).filter(models.User.is_active == True).count()
    unread = db.query(models.Notification).filter(models.Notification.is_read == False).count()

    return {
        "total_cases": total,
        "active_cases": active,
        "urgent_cases": urgent,
        "resolved_cases": resolved,
        "pending_cases": pending,
        "total_officers": officers,
        "unread_notifications": unread
    }

def get_monthly_stats(db: Session, year: int = None):
    if year is None:
        year = datetime.now().year
    results = db.query(
        extract("month", models.Report.date_reported).label("month"),
        func.count(models.Report.id).label("count")
    ).filter(
        extract("year", models.Report.date_reported) == year
    ).group_by("month").order_by("month").all()

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    stats = []
    for row in results:
        month_idx = int(row.month) - 1
        if 0 <= month_idx < 12:
            stats.append({"month": months[month_idx], "count": row.count})
    return stats

def get_priority_breakdown(db: Session):
    return db.query(
        models.Report.priority,
        func.count(models.Report.id).label("count")
    ).group_by(models.Report.priority).all()

def get_status_breakdown(db: Session):
    return db.query(
        models.Report.status,
        func.count(models.Report.id).label("count")
    ).group_by(models.Report.status).all()

def get_officer_workload(db: Session):
    officers = db.query(models.User).filter(models.User.role.in_(["officer", "admin"])).all()
    result = []
    for officer in officers:
        assigned = db.query(models.Report).filter(
            models.Report.assigned_to == officer.id
        ).count()
        active = db.query(models.Report).filter(
            models.Report.assigned_to == officer.id,
            models.Report.status.in_(["Assigned", "Ongoing", "Monitoring"])
        ).count()
        resolved = db.query(models.Report).filter(
            models.Report.assigned_to == officer.id,
            models.Report.status.in_(["Resolved", "Archived"])
        ).count()
        result.append({
            "officer_id": officer.id,
            "officer_name": officer.full_name,
            "assigned_count": assigned,
            "active_count": active,
            "resolved_count": resolved
        })
    return result

def get_recent_activities(db: Session, limit: int = 10):
    return db.query(models.CaseActivity).order_by(
        models.CaseActivity.created_at.desc()
    ).limit(limit).all()

def get_all_cases_full(db: Session):
    return db.query(models.Report).order_by(models.Report.date_reported.desc()).all()
