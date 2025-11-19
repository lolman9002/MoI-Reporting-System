"""
Central import point for all models.
Import all models here to ensure they're registered with SQLAlchemy.
"""

from app.core.database import Base

# Import all models in the correct order
from app.models.user import User
from app.models.report import Report
from app.models.attachment import Attachment

# Export for convenience
__all__ = ["Base", "User", "Report", "Attachment"]