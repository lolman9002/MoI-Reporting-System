from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Import attachment schemas to nest them inside reports
from app.schemas.attachment import AttachmentCreate, AttachmentResponse

# Enums must match your SQL constraints exactly
class ReportStatus(str, Enum):
    SUBMITTED = "Submitted"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "InProgress"
    RESOLVED = "Resolved"
    REJECTED = "Rejected"

class ReportCategory(str, Enum):
    INFRASTRUCTURE = "infrastructure"
    UTILITIES = "utilities"
    CRIME = "crime"
    TRAFFIC = "traffic"
    PUBLIC_NUISANCE = "public_nuisance"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"

# Base schema with common fields
class ReportBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    descriptionText: str = Field(..., min_length=10)
    
    # Optional in Base because AI might fill it later, 
    # but usually required for display.
    categoryId: Optional[ReportCategory] = None 

# Schema for CREATING a report (Input)
class ReportCreate(ReportBase):
    # [cite_start]REPLACED latitude/longitude with text/link string [cite: 41]
    location: str = Field(..., description="Physical address, landmark, or Google Maps link")
    
    transcribedVoiceText: Optional[str] = None
    
    # [cite_start]Anonymous Reporting Fields [cite: 34]
    isAnonymous: bool = Field(False, description="True if user wants to remain anonymous")
    hashedDeviceId: Optional[str] = Field(None, description="Required if isAnonymous=True for tracking")
    
    # Nested Attachments: Client sends list of file metadata with the report
    attachments: List[AttachmentCreate] = []

# Schema for UPDATING a report (General Input)
class ReportUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    descriptionText: Optional[str] = Field(None, min_length=10)
    status: Optional[ReportStatus] = None
    categoryId: Optional[ReportCategory] = None
    location: Optional[str] = None 

# --- NEW: Schema for STATUS ONLY updates (Required by your API) ---
class ReportStatusUpdate(BaseModel):
    status: ReportStatus
    notes: Optional[str] = None # For admin notes/resolution details

# Schema for READING a report (Output)
class ReportResponse(ReportBase):
    reportId: str
    status: ReportStatus
    location: str  # Matches [locationRaw] in DB
    aiConfidence: Optional[float] = None
    createdAt: datetime
    updatedAt: datetime
    userId: Optional[str] = None
    transcribedVoiceText: Optional[str] = None
    
    # Returns full attachment objects
    attachments: List[AttachmentResponse] = []

    class Config:
        from_attributes = True

# --- NEW: Schema for LIST responses (Required by your API) ---
class ReportListResponse(BaseModel):
    reports: List[ReportResponse]
    total: int
    page: int
    pageSize: int
    totalPages: int