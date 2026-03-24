from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    victim_name = Column(String)
    contact_number = Column(String)
    incident_type = Column(String)
    description = Column(Text)
    location = Column(Text)
    date_reported = Column(TIMESTAMP, server_default=func.now())
    status = Column(String, default="Pending")
    file_path = Column(String, nullable=True)

file_path = Column(String, nullable=True)