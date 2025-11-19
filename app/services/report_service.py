import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.report import Report
from app.models.attachment import Attachment

from app.schemas.report import (
    ReportCreate, 
    ReportResponse, 
    ReportListResponse, 
    ReportStatusUpdate
)

def utcnow():
    """Helper to get current UTC time."""
    return datetime.now(timezone.utc)

class ReportService:
    """Business logic for reports (Async)."""
    
    @staticmethod
    async def create_report(
        db: AsyncSession, 
        report_data: ReportCreate, 
        user_id: Optional[str] = None
    ) -> ReportResponse:
        """Create a new report with attachments."""
        
        # Generate unique ID
        report_id = f"R-{uuid.uuid4().hex[:8].upper()}"
        
        # Create Report object
        db_report = Report(
            reportId=report_id,
            title=report_data.title,
            descriptionText=report_data.descriptionText,
            locationRaw=report_data.location,
            categoryId=report_data.categoryId.value if report_data.categoryId else "other",
            userId=user_id,
            transcribedVoiceText=report_data.transcribedVoiceText,
            status="Submitted",
            aiConfidence=None,
            createdAt=utcnow(),
            updatedAt=utcnow()
        )
        
        # Add to session first
        db.add(db_report)
        
        # Create attachments
        attachment_orms = []
        for att_data in report_data.attachments:
            new_attachment = Attachment(
                attachmentId=str(uuid.uuid4()),
                reportId=report_id,
                blobStorageUri=str(att_data.blobStorageUri),
                mimeType=att_data.mimeType,
                fileType=att_data.fileType,
                fileSizeBytes=att_data.fileSizeBytes
            )
            db.add(new_attachment)
            attachment_orms.append(new_attachment)
        
        # Commit everything
        try:
            await db.commit()
            
            # Refresh to get server defaults
            await db.refresh(db_report)
            
            # Build response manually (avoid lazy loading)
            attachment_responses = [
                {
                    "attachmentId": att.attachmentId,
                    "reportId": att.reportId,
                    "blobStorageUri": str(att.blobStorageUri),
                    "mimeType": att.mimeType,
                    "fileType": att.fileType,
                    "fileSizeBytes": att.fileSizeBytes
                }
                for att in attachment_orms
            ]
            
            return ReportResponse(
                reportId=db_report.reportId,
                title=db_report.title,
                descriptionText=db_report.descriptionText,
                categoryId=db_report.categoryId,
                status=db_report.status,
                location=db_report.locationRaw,
                aiConfidence=db_report.aiConfidence,
                createdAt=db_report.createdAt,
                updatedAt=db_report.updatedAt,
                userId=db_report.userId,
                transcribedVoiceText=db_report.transcribedVoiceText,
                attachments=attachment_responses
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to create report: {str(e)}"
            )

    @staticmethod
    async def get_report(db: AsyncSession, report_id: str) -> Optional[ReportResponse]:
        """Get a single report by ID with attachments eagerly loaded."""
        
        # Use selectinload to eagerly load attachments
        stmt = (
            select(Report)
            .options(selectinload(Report.attachments))
            .where(Report.reportId == report_id)
        )
        
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()
        
        if not report:
            return None
        
        # Build attachment responses
        attachment_responses = [
            {
                "attachmentId": att.attachmentId,
                "reportId": att.reportId,
                "blobStorageUri": str(att.blobStorageUri),
                "mimeType": att.mimeType,
                "fileType": att.fileType,
                "fileSizeBytes": att.fileSizeBytes
            }
            for att in report.attachments
        ]
        
        return ReportResponse(
            reportId=report.reportId,
            title=report.title,
            descriptionText=report.descriptionText,
            categoryId=report.categoryId,
            status=report.status,
            location=report.locationRaw,
            aiConfidence=report.aiConfidence,
            createdAt=report.createdAt,
            updatedAt=report.updatedAt,
            userId=report.userId,
            transcribedVoiceText=report.transcribedVoiceText,
            attachments=attachment_responses
        )
    
    @staticmethod
    async def list_reports(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 10,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> ReportListResponse:
        """List reports with pagination and eager loading."""
        
        # Base query with eager loading
        stmt = select(Report).options(selectinload(Report.attachments))
        
        # Apply filters
        if status:
            stmt = stmt.where(Report.status == status)
        if category:
            stmt = stmt.where(Report.categoryId == category)
        
        # Get total count (without eager loading for efficiency)
        count_stmt = select(func.count()).select_from(
            select(Report).where(
                *(
                    [Report.status == status] if status else []
                    + [Report.categoryId == category] if category else []
                )
            ).subquery()
        )
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()
        
        # Apply pagination
        stmt = stmt.order_by(Report.createdAt.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        reports = result.scalars().all()
        
        # Convert to response schemas
        report_responses = []
        for r in reports:
            attachment_responses = [
                {
                    "attachmentId": att.attachmentId,
                    "reportId": att.reportId,
                    "blobStorageUri": str(att.blobStorageUri),
                    "mimeType": att.mimeType,
                    "fileType": att.fileType,
                    "fileSizeBytes": att.fileSizeBytes
                }
                for att in r.attachments
            ]
            
            report_responses.append(
                ReportResponse(
                    reportId=r.reportId,
                    title=r.title,
                    descriptionText=r.descriptionText,
                    categoryId=r.categoryId,
                    status=r.status,
                    location=r.locationRaw,
                    aiConfidence=r.aiConfidence,
                    createdAt=r.createdAt,
                    updatedAt=r.updatedAt,
                    userId=r.userId,
                    transcribedVoiceText=r.transcribedVoiceText,
                    attachments=attachment_responses
                )
            )
        
        return ReportListResponse(
            reports=report_responses,
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            pageSize=limit,
            totalPages=(total + limit - 1) // limit if limit > 0 else 1
        )
    
    @staticmethod
    async def update_report_status(
        db: AsyncSession,
        report_id: str,
        status_update: ReportStatusUpdate
    ) -> Optional[ReportResponse]:
        """Update report status."""
        
        stmt = (
            select(Report)
            .options(selectinload(Report.attachments))
            .where(Report.reportId == report_id)
        )
        
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()
        
        if not report:
            return None
        
        # Update fields
        report.status = status_update.status.value
        report.updatedAt = utcnow()
        
        try:
            await db.commit()
            await db.refresh(report)
            
            # Build attachment responses
            attachment_responses = [
                {
                    "attachmentId": att.attachmentId,
                    "reportId": att.reportId,
                    "blobStorageUri": str(att.blobStorageUri),
                    "mimeType": att.mimeType,
                    "fileType": att.fileType,
                    "fileSizeBytes": att.fileSizeBytes
                }
                for att in report.attachments
            ]
            
            return ReportResponse(
                reportId=report.reportId,
                title=report.title,
                descriptionText=report.descriptionText,
                categoryId=report.categoryId,
                status=report.status,
                location=report.locationRaw,
                aiConfidence=report.aiConfidence,
                createdAt=report.createdAt,
                updatedAt=report.updatedAt,
                userId=report.userId,
                transcribedVoiceText=report.transcribedVoiceText,
                attachments=attachment_responses
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to update report status: {str(e)}"
            )
    
    @staticmethod
    async def delete_report(db: AsyncSession, report_id: str) -> bool:
        """Delete a report."""
        
        stmt = select(Report).where(Report.reportId == report_id)
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()
        
        if not report:
            return False
        
        try:
            await db.delete(report)
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to delete report: {str(e)}"
            )