from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from enum import Enum

class FileType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

# Schema for INPUT (Client -> Server)
class AttachmentCreate(BaseModel):
    blobStorageUri: HttpUrl 
    mimeType: str = Field(..., pattern=r'^[a-z]+/[a-z0-9\-\+\.]+$') 
    fileType: FileType
    #  50MB limit is a smart safety check
    fileSizeBytes: int = Field(..., gt=0, le=52428800) 

# Schema for OUTPUT (Server -> Client)
class AttachmentResponse(BaseModel):
    attachmentId: str
    reportId: str  # The response should confirm the link
    blobStorageUri: HttpUrl
    mimeType: str
    fileType: FileType
    fileSizeBytes: int

    class Config:
        from_attributes = True