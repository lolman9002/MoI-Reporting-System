from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportListResponse,
    ReportStatusUpdate,
    ReportStatus,
    ReportCategory
)
# Make sure to import the Service we created earlier
from app.services.report_service import ReportService

router = APIRouter()

@router.post(
    "/",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new report",
    description="Create a new incident report with location text and attachments"
)
async def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db)
    # TODO: Add 'current_user' dependency later to pass user_id
):
    """
    Submit a new incident report.
    
    - **title**: Short title of the incident
    - **descriptionText**: Detailed description
    - [cite_start]**location**: Address text or Google Maps link (Replaces Lat/Lon) [cite: 41]
    - **categoryId**: Category of the incident (Optional, AI can detect)
    - **transcribedVoiceText**: Optional voice transcription
    - **attachments**: List of file metadata (images/videos)
    - [cite_start]**isAnonymous**: Flag for anonymous reporting [cite: 34]
    """
    try:
        # We pass None for user_id for now. 
        # Later, you will replace 'None' with 'current_user.userId'
        return ReportService.create_report(db, report, user_id=None)
    except Exception as e:
        # Catch unexpected errors (like DB connection issues)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create report: {str(e)}"
        )

@router.get(
    "/",
    response_model=ReportListResponse,
    summary="List all reports",
    description="Get paginated list of reports with optional filters"
)
async def list_reports(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum records to return"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    category: Optional[ReportCategory] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Get list of reports with pagination and filters.
    """
    # Extract string value from Enum if present
    status_value = status.value if status else None
    category_value = category.value if category else None
    
    return ReportService.list_reports(
        db, 
        skip=skip, 
        limit=limit,
        status=status_value,
        category=category_value
    )

@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report by ID",
    description="Retrieve detailed information including attachments"
)
async def get_report(
    report_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single report by its ID.
    """
    report = ReportService.get_report(db, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    
    return report

@router.put(
    "/{report_id}/status",
    response_model=ReportResponse,
    summary="Update report status",
    description="Change the status of a report (for officials)"
)
async def update_report_status(
    report_id: str,
    status_update: ReportStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update the status of a report (e.g., to 'Resolved').
    """
    report = ReportService.update_report_status(db, report_id, status_update)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    
    return report

@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a report",
    description="Permanently delete a report and its attachments"
)
async def delete_report(
    report_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a report permanently.
    """
    success = ReportService.delete_report(db, report_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    
    return None