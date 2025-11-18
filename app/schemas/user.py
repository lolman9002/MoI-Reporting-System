from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CITIZEN = "citizen"
    OFFICER = "officer"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    role: UserRole = UserRole.CITIZEN

class UserCreate(UserBase):
    isAnonymous: bool = False
    hashedDeviceId: Optional[str] = None

class UserResponse(UserBase):
    userId: str
    isAnonymous: bool
    createdAt: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None