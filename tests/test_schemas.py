import pytest
from pydantic import ValidationError
from app.schemas.report import ReportCreate, ReportCategory
from app.schemas.attachment import AttachmentCreate, FileType

# ==========================================
# 1. TEST ATTACHMENTS
# ==========================================

def test_valid_attachment():
    """Test creating a perfectly valid attachment."""
    valid_data = {
        "blobStorageUri": "https://myaccount.blob.core.windows.net/container/image.png",
        "mimeType": "image/png",
        "fileType": "image",
        "fileSizeBytes": 1024  # 1 KB
    }
    attachment = AttachmentCreate(**valid_data)
    assert str(attachment.blobStorageUri) == valid_data["blobStorageUri"]
    assert attachment.fileSizeBytes == 1024

def test_attachment_invalid_url():
    """Test that a bad URL raises a validation error."""
    invalid_data = {
        "blobStorageUri": "not_a_url",  # <--- INVALID
        "mimeType": "image/png",
        "fileType": "image",
        "fileSizeBytes": 1024
    }
    with pytest.raises(ValidationError) as excinfo:
        AttachmentCreate(**invalid_data)
    assert "url" in str(excinfo.value)

def test_attachment_file_too_large():
    """Test that a file > 50MB fails."""
    invalid_data = {
        "blobStorageUri": "https://valid-url.com/vid.mp4",
        "mimeType": "video/mp4",
        "fileType": "video",
        "fileSizeBytes": 52_428_801  # <--- 50MB + 1 Byte (INVALID)
    }
    with pytest.raises(ValidationError) as excinfo:
        AttachmentCreate(**invalid_data)
    # Pydantic error for 'le' (less than or equal)
    assert "less than or equal to 52428800" in str(excinfo.value)

def test_attachment_bad_mime_regex():
    """Test that the regex catches invalid MIME types."""
    invalid_data = {
        "blobStorageUri": "https://valid-url.com/file",
        "mimeType": "bad_mime_type",  # <--- Missing slash (INVALID)
        "fileType": "other",
        "fileSizeBytes": 100
    }
    with pytest.raises(ValidationError) as excinfo:
        AttachmentCreate(**invalid_data)
    assert "string_pattern_mismatch" in str(excinfo.value)  # Regex failure

# ==========================================
# 2. TEST REPORTS
# ==========================================

def test_valid_report_creation():
    """Test creating a full report with location text and attachments."""
    valid_report = {
        "title": "Broken Streetlight",
        "descriptionText": "The light is flickering heavily.",
        "categoryId": "infrastructure",
        "location": "Corner of King Faisal St and Main St",  # <--- Text Location
        "isAnonymous": True,
        "hashedDeviceId": "abc123hash",
        "attachments": [
            {
                "blobStorageUri": "https://azure.com/evidence.jpg",
                "mimeType": "image/jpeg",
                "fileType": "image",
                "fileSizeBytes": 5000
            }
        ]
    }
    report = ReportCreate(**valid_report)
    assert report.location == "Corner of King Faisal St and Main St"
    assert len(report.attachments) == 1
    assert report.isAnonymous is True

def test_report_missing_location():
    """Test that location is mandatory."""
    invalid_report = {
        "title": "No Location Report",
        "descriptionText": "I forgot to say where.",
        "categoryId": "other"
        # MISSING "location" field
    }
    with pytest.raises(ValidationError) as excinfo:
        ReportCreate(**invalid_report)
    assert "location" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)

def test_report_short_description():
    """Test that description length validation works."""
    invalid_report = {
        "title": "Short",
        "descriptionText": "Too short",  # <--- Less than 10 chars
        "location": "Cairo",
        "categoryId": "other"
    }
    with pytest.raises(ValidationError) as excinfo:
        ReportCreate(**invalid_report)
    assert "descriptionText" in str(excinfo.value)