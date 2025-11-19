from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Attachment(Base):
    __tablename__ = "Attachment"  # Matches SQL table name exactly

    # Primary Key - matches [attachmentId] in SQL
    attachmentId = Column(String(450), primary_key=True, index=True, name="attachmentId")
    
    # Foreign Key - matches [reportId] in SQL and references Report.reportId
    reportId = Column(
        String(450), 
        ForeignKey("Report.reportId", ondelete="CASCADE"), 
        nullable=False,
        name="reportId"
    )
    
    # Metadata Columns - match SQL column names exactly
    blobStorageUri = Column(String(2048), nullable=False, name="blobStorageUri")
    mimeType = Column(String(100), nullable=False, name="mimeType")
    fileType = Column(String(50), nullable=False, name="fileType")
    fileSizeBytes = Column(BigInteger, nullable=False, name="fileSizeBytes")

    # Relationship - use string reference
    report = relationship("Report", back_populates="attachments")

    def __repr__(self):
        return f"<Attachment(attachmentId={self.attachmentId}, reportId={self.reportId}, fileType={self.fileType})>"