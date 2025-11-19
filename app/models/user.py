from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "User"  # Matches SQL table name exactly

    # Primary Key - matches [userId] in SQL
    userId = Column(String(450), primary_key=True, index=True, name="userId")
    
    # Attributes - match SQL column names exactly
    isAnonymous = Column(Boolean, nullable=False, default=False, name="isAnonymous")
    createdAt = Column(DateTime, nullable=False, server_default=func.getutcdate(), name="createdAt")
    role = Column(String(50), nullable=False, default="citizen", name="role")
    
    email = Column(String(256), nullable=True, name="email")
    phoneNumber = Column(String(20), nullable=True, name="phoneNumber")
    hashedDeviceId = Column(String(256), nullable=True, name="hashedDeviceId")

    # Relationships - use string references to avoid circular import
    reports = relationship("Report", back_populates="user")

    def __repr__(self):
        return f"<User(userId={self.userId}, isAnonymous={self.isAnonymous}, role={self.role})>"