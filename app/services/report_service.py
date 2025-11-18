from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

# Import your Database Models
from app.models.report import Report
from app.models.user import User
from app.models.attachment import Attachment

# Import your Pydantic Schemas
from app.schemas.report import (
    ReportCreate, 
    ReportUpdate, 
    ReportResponse,
    ReportListResponse,
    ReportStatusUpdate
)

class ReportService:
    """Business logic for reports"""
    
    @staticmethod
    def create_report(
        db: Session, 
        report_data: ReportCreate, 
        user_id: Optional[str] = None
    ) -> ReportResponse:
        """
        Create a new report, including its location string and attachments.
        """
        
        # 1. Generate unique ID for the report
        report_id = f"R-{uuid.uuid4().hex[:8].upper()}"
        
        # 2. Create the Report database object
        db_report = Report(
            reportId=report_id,
            title=report_data.title,
            descriptionText=report_data.descriptionText,
            
            # MAPPING: Schema 'location' -> DB 'locationRaw'
            locationRaw=report_data.location, 
            
            # Handle Enum value
            categoryId=report_data.categoryId.value if report_data.categoryId else "other",
            
            userId=user_id,
            transcribedVoiceText=report_data.transcribedVoiceText,
            status="Submitted",
            
            # AI Confidence (Simulated for now, or passed if you have an AI service running before this)
            aiConfidence=None, 
            
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow()
        )
        
        db.add(db_report)

        # 3. Process Nested Attachments
        # The schema 'report_data.attachments' contains a list of file metadata
        for att_data in report_data.attachments:
            new_attachment = Attachment(
                attachmentId=str(uuid.uuid4()),
                reportId=report_id, # Link to the new report
                blobStorageUri=str(att_data.blobStorageUri), # Convert HttpUrl to string
                mimeType=att_data.mimeType,
                fileType=att_data.fileType.value, # Enum to string
                fileSizeBytes=att_data.fileSizeBytes
            )
            db.add(new_attachment)
        
        # 4. Commit Transaction (Saves Report + Attachments together)
        db.commit()
        db.refresh(db_report)
        
        # 5. Return Pydantic Response
        # Pydantic's from_attributes=True will handle the conversion of SQLAlchemy objects
        return ReportResponse.model_validate(db_report)
    
    @staticmethod
    def get_report(db: Session, report_id: str) -> Optional[ReportResponse]:
        """Get a single report by ID with its attachments"""
        report = db.query(Report).filter(Report.reportId == report_id).first()
        
        if not report:
            return None
        
        # Pydantic v2 syntax for converting ORM model to Schema
        # This automatically maps 'report.locationRaw' to 'schema.location' 
        # because we defined the alias or mapping in the Schema Config if needed,
        # BUT since names differ, we explicitly map them below if not using aliases.
        
        return ReportResponse(
            reportId=report.reportId,
            title=report.title,
            descriptionText=report.descriptionText,
            categoryId=report.categoryId,
            status=report.status,
            
            # EXPLICIT MAPPING: DB 'locationRaw' -> Schema 'location'
            location=report.locationRaw,
            
            aiConfidence=report.aiConfidence,
            createdAt=report.createdAt,
            updatedAt=report.updatedAt,
            userId=report.userId,
            transcribedVoiceText=report.transcribedVoiceText,
            
            # SQLAlchemy relationship 'attachments' is converted to list
            attachments=report.attachments 
        )
    
    @staticmethod
    def list_reports(
        db: Session, 
        skip: int = 0, 
        limit: int = 10,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> ReportListResponse:
        """List reports with pagination and filters"""
        
        query = db.query(Report)
        
        # Apply filters
        if status:
            query = query.filter(Report.status == status)
        if category:
            query = query.filter(Report.categoryId == category)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        reports = query.order_by(Report.createdAt.desc()).offset(skip).limit(limit).all()
        
        # Convert to response schemas
        report_responses = []
        for report in reports:
            report_responses.append(
                ReportResponse(
                    reportId=report.reportId,
                    title=report.title,
                    descriptionText=report.descriptionText,
                    categoryId=report.categoryId,
                    status=report.status,
                    location=report.locationRaw, # Mapping DB -> Schema
                    aiConfidence=report.aiConfidence,
                    createdAt=report.createdAt,
                    updatedAt=report.updatedAt,
                    userId=report.userId,
                    transcribedVoiceText=report.transcribedVoiceText,
                    attachments=report.attachments
                )
            )
        
        return ReportListResponse(
            reports=report_responses,
            total=total,
            page=skip // limit + 1,
            pageSize=limit,
            totalPages=(total + limit - 1) // limit
        )
    
    @staticmethod
    def update_report_status(
        db: Session,
        report_id: str,
        status_update: ReportStatusUpdate
    ) -> Optional[ReportResponse]:
        """Update report status"""
        
        report = db.query(Report).filter(Report.reportId == report_id).first()
        
        if not report:
            return None
        
        report.status = status_update.status.value
        report.updatedAt = datetime.utcnow()
        # Note: Admin might add notes here, handled if you add a 'resolutionNotes' column later
        
        db.commit()
        db.refresh(report)
        
        # Reuse get logic to ensure consistent formatting
        return ReportService.get_report(db, report_id)
    
    @staticmethod
    def delete_report(db: Session, report_id: str) -> bool:
        """Delete a report"""
        report = db.query(Report).filter(Report.reportId == report_id).first()
        
        if not report:
            return False
        
        # Because we set cascade="all, delete-orphan" in the Model, 
        # deleting the report will automatically delete associated Attachments.
        db.delete(report)
        db.commit()
        return True