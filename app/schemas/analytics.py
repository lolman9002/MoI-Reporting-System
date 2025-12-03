from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class MonthlyCategoryCount(BaseModel):
    year: int
    month: int
    category: str
    count: int

class UserListResponse(BaseModel):
    """Schema for listing users (admin view)"""
    user_id: str
    email: Optional[str]
    phone_number: Optional[str]
    role: str
    is_anonymous: bool
    created_at: datetime
    hashed_device_id: Optional[str]
    password_hash: Optional[str]  # Careful with this - maybe don't expose!


class UserDemographicResponse(BaseModel):
    """Response for demographic breakdown"""
    role: str
    is_anonymous: bool
    account_age_segment: str
    user_count: int
    
    class Config:
        from_attributes = True



class DashboardStatsResponse(BaseModel):
    """Response schema for dashboard statistics"""
    totalReports: int
    hotReports: int
    coldReports: int
    statusBreakdown: Dict[str, int]
    categoryBreakdown: Dict[str, int]
    avgAiConfidence: float
    anonymousReports: int
    registeredReports: int
    
    monthlyCategoryCounts: List[MonthlyCategoryCount]
    demographiCounts : List[UserDemographicResponse]
    UsersList : List[UserListResponse]

    class Config:
        from_attributes = True