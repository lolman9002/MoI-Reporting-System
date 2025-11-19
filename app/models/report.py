from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, func
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class Report(Base):
    __tablename__ = "Report"  # Matches SQL table name exactly

    # Primary Key - matches [reportId] in SQL
    reportId = Column(String(450), primary_key=True, index=True, name="reportId")
    
    # Foreign Key - matches [userId] in SQL and references User.userId
    userId = Column(
        String(450), 
        ForeignKey("User.userId", ondelete="SET NULL"), 
        nullable=True,
        name="userId"
    )
    
    # Core Data Columns - match SQL column names exactly
    title = Column(String(500), nullable=False, name="title")
    descriptionText = Column(Text, nullable=False, name="descriptionText")
    
    # Location field - matches [locationRaw] in SQL
    locationRaw = Column(String(2048), nullable=True, name="locationRaw")
    
    status = Column(String(50), nullable=False, default="Submitted", name="status")
    categoryId = Column(String(100), nullable=False, name="categoryId")

    # Metadata & AI
    aiConfidence = Column(
        Float, 
        CheckConstraint('aiConfidence >= 0 AND aiConfidence <= 1'), 
        nullable=True,
        name="aiConfidence"
    )
    transcribedVoiceText = Column(Text, nullable=True, name="transcribedVoiceText")

    # Timestamps - match SQL column names exactly
    createdAt = Column(
        DateTime, 
        nullable=False, 
        server_default=func.getutcdate(),
        name="createdAt"
    )
    updatedAt = Column(
        DateTime, 
        nullable=False, 
        server_default=func.getutcdate(),
        onupdate=func.getutcdate(),
        name="updatedAt"
    )
    
    # Relationships - use string references
    user = relationship("User", back_populates="reports")
    attachments = relationship("Attachment", back_populates="report", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Report(reportId={self.reportId}, title={self.title}, status={self.status})>"