from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(String(50), default="officer")
    barangay = Column(String(200), nullable=True)
    contact_number = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    assigned_cases = relationship("Report", back_populates="assigned_officer", foreign_keys="Report.assigned_to")
    activities = relationship("CaseActivity", back_populates="performer", foreign_keys="CaseActivity.performed_by")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    victim_name = Column(String(200), nullable=False)
    contact_number = Column(String(50), nullable=False)
    incident_type = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(300), nullable=False)

    date_reported = Column(TIMESTAMP, server_default=func.now())
    status = Column(String(50), default="Submitted")
    file_path = Column(String(500), nullable=True)

    # FIXED: case_id is now STRING (VAWC-2026-0002)
    case_id = Column(String(50), unique=True, nullable=True)

    priority = Column(String(20), default="LOW")
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    case_notes = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    assigned_officer = relationship(
        "User",
        back_populates="assigned_cases",
        foreign_keys=[assigned_to]
    )

    case_record = relationship("Case", back_populates="report", foreign_keys="Case.report_id", uselist=False)

    notifications = relationship(
        "Notification",
        back_populates="case",
        foreign_keys="Notification.case_id"
    )

    referrals = relationship(
        "Referral",
        back_populates="case",
        foreign_keys="Referral.case_id"
    )

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, unique=True)
    status = Column(String(50), default="Submitted")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    report = relationship("Report", back_populates="case_record", foreign_keys=[report_id])
    activities = relationship("CaseActivity", back_populates="case", foreign_keys="CaseActivity.case_id")


class CaseActivity(Base):
    __tablename__ = "case_activities"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    action = Column(String(200), nullable=False)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    case = relationship("Case", back_populates="activities", foreign_keys=[case_id])
    performer = relationship("User", back_populates="activities", foreign_keys=[performed_by])


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
    message = Column(Text, nullable=False)
    recipient_role = Column(String(50), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    case = relationship("Report", back_populates="notifications", foreign_keys=[case_id])


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(TIMESTAMP, server_default=func.now())

    case = relationship("Report", backref="evidence_list", foreign_keys=[case_id])
    uploader = relationship("User", backref="uploaded_evidence", foreign_keys=[uploaded_by])


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    referred_to = Column(String(100), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(50), default="Pending")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    case = relationship("Report", back_populates="referrals", foreign_keys=[case_id])
