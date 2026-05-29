from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

# =====================================================================
# EXISTING SCHEMAS (PRESERVED)
# =====================================================================

class ReportCreate(BaseModel):
    victim_name: str = Field(..., min_length=1, max_length=200, description="Full name of the victim")
    contact_number: str = Field(..., min_length=7, max_length=50, description="Contact number of the victim")
    incident_type: str = Field(..., min_length=1, max_length=200, description="Type of incident")
    description: str = Field(..., min_length=10, max_length=5000, description="Detailed description of the incident")
    location: str = Field(..., min_length=1, max_length=300, description="Location of the incident")


class ReportResponse(ReportCreate):
    id: int
    status: str
    model_config = {"from_attributes": True}


class ReportFull(ReportCreate):
    id: int
    case_id: Optional[str] = None
    status: str
    priority: str
    assigned_to: Optional[int] = None
    file_path: Optional[str] = None
    case_notes: Optional[str] = None
    resolution_notes: Optional[str] = None
    date_reported: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ReportUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=20)
    assigned_to: Optional[int] = None
    case_notes: Optional[str] = Field(None, max_length=10000)
    resolution_notes: Optional[str] = Field(None, max_length=10000)


# =====================================================================
# AUTH SCHEMAS
# =====================================================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, description="Unique username for login")
    email: str = Field(..., max_length=200, description="Valid email address")
    password: str = Field(..., min_length=6, max_length=200, description="Password (min 6 characters)")
    full_name: str = Field(..., min_length=1, max_length=200, description="Full name of the user")
    role: str = Field("officer", max_length=50, description="User role: admin or officer")
    barangay: Optional[str] = Field(None, max_length=200, description="Assigned barangay")
    contact_number: Optional[str] = Field(None, max_length=50, description="Contact number")
    admin_secret: Optional[str] = Field(None, max_length=200, description="Secret key required for admin registration")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must contain only letters, numbers, and underscores")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    role: Optional[str] = Field(None, max_length=50)
    barangay: Optional[str] = Field(None, max_length=200)
    contact_number: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email format")
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    account_status: str = "approved"
    barangay: Optional[str] = None
    contact_number: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password for login")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# =====================================================================
# CASE ACTIVITY
# =====================================================================

class CaseActivityResponse(BaseModel):
    id: int
    case_id: int
    action: str
    performed_by: Optional[int] = None
    performed_by_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# =====================================================================
# NOTIFICATION
# =====================================================================

class NotificationResponse(BaseModel):
    id: int
    case_id: Optional[int] = None
    message: str
    recipient_role: str
    is_read: bool
    is_archived: bool = False
    is_deleted: bool = False
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# =====================================================================
# EVIDENCE
# =====================================================================

class EvidenceResponse(BaseModel):
    id: int
    case_id: int
    filename: str
    file_path: str
    file_type: Optional[str] = None
    uploaded_by: Optional[int] = None
    uploaded_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# =====================================================================
# REFERRAL
# =====================================================================

class ReferralCreate(BaseModel):
    referred_to: str = Field(..., max_length=100, description="Agency to refer to (PNP, DSWD, Hospital, Barangay)")
    reason: str = Field(..., min_length=10, max_length=2000, description="Reason for referral")


class ReferralUpdate(BaseModel):
    status: str = Field(..., max_length=50, description="Referral status: Pending, Accepted, Completed")


class ReferralResponse(BaseModel):
    id: int
    case_id: int
    referred_to: str
    reason: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# =====================================================================
# DASHBOARD / ANALYTICS
# =====================================================================

class DashboardStats(BaseModel):
    total_cases: int
    active_cases: int
    urgent_cases: int
    resolved_cases: int
    pending_cases: int
    total_officers: int
    unread_notifications: int


class MonthlyStats(BaseModel):
    month: str
    count: int


class OfficerWorkload(BaseModel):
    officer_id: int
    officer_name: str
    assigned_count: int
    active_count: int
    resolved_count: int


# =====================================================================
# GENERIC RESPONSE
# =====================================================================

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
