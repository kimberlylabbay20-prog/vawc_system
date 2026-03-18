from pydantic import BaseModel

class ReportCreate(BaseModel):
    victim_name: str
    contact_number: str
    incident_type: str
    description: str
    location: str


class ReportResponse(ReportCreate):
    id: int
    status: str

    class Config:
        orm_mode = True