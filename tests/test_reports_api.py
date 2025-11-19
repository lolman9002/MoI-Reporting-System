from fastapi.testclient import TestClient
from app.main import app

# Initialize client with the app
client = TestClient(app)

def test_create_report():
    """Test creating a new report"""
    # Payload matches your new Schema (Location string + Attachments list)
    payload = {
        "title": "Test Pothole",
        "descriptionText": "This is a test pothole report for testing purposes",
        "categoryId": "infrastructure",
        "location": "King Faisal Street, Giza",  # Using text location
        "isAnonymous": False,
        "attachments": [] # Required by schema, even if empty
    }

    response = client.post("/api/v1/reports/", json=payload)
    
    # Debug print if it fails
    if response.status_code != 201:
        print(f"❌ Create Failed: {response.text}")

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Pothole"
    assert data["status"] == "Submitted"
    assert "reportId" in data
    
    print(f"✓ Created report: {data['reportId']}")
    return data["reportId"]

def test_list_reports():
    """Test listing reports"""
    # Create one first to ensure list isn't empty
    test_create_report()
    
    response = client.get("/api/v1/reports/?skip=0&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify ReportListResponse structure
    assert "reports" in data
    assert "total" in data
    assert len(data["reports"]) > 0
    print(f"✓ Listed {len(data['reports'])} reports")

def test_get_report():
    """Test getting a specific report"""
    report_id = test_create_report()
    
    response = client.get(f"/api/v1/reports/{report_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["reportId"] == report_id
    print(f"✓ Retrieved report: {report_id}")

def test_update_report_status():
    """Test updating report status"""
    report_id = test_create_report()
    
    # Payload matches ReportStatusUpdate schema
    payload = {
        "status": "Assigned",
        "notes": "Assigned to maintenance team"
    }
    
    response = client.put(
        f"/api/v1/reports/{report_id}/status",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Assigned"
    print(f"✓ Updated report status: {report_id}")

if __name__ == "__main__":
    print("🧪 Testing Report API Endpoints...")
    print("=" * 50)
    try:
        test_create_report()
        test_list_reports()
        test_get_report()
        test_update_report_status()
        print("=" * 50)
        print("✅ All tests passed!")
    except AssertionError as e:
        print(f"❌ Assertion Failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")