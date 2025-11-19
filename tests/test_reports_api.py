import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_report(client: AsyncClient):
    """Test creating a new report."""
    payload = {
        "title": "Test Pothole",
        "descriptionText": "This is a test pothole report for testing purposes",
        "categoryId": "infrastructure",
        "location": "King Faisal Street, Giza",
        "isAnonymous": False,
        "attachments": []
    }

    response = await client.post("/api/v1/reports/", json=payload)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    
    data = response.json()
    assert data["title"] == "Test Pothole"
    assert data["status"] == "Submitted"
    assert "reportId" in data
    
    print(f"✓ Created report: {data['reportId']}")
    return data["reportId"]

@pytest.mark.asyncio
async def test_list_reports(client: AsyncClient):
    """Test listing reports."""
    # Create a report first
    create_response = await client.post(
        "/api/v1/reports/",
        json={
            "title": "Test Report for List",
            "descriptionText": "Test description for listing",
            "categoryId": "infrastructure",
            "location": "Test Location",
            "isAnonymous": False,
            "attachments": []
        }
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["reportId"]
    
    # List reports
    response = await client.get("/api/v1/reports/?skip=0&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "reports" in data
    assert "total" in data
    assert isinstance(data["reports"], list)
    assert len(data["reports"]) > 0
    
    # Verify structure
    found = False
    for report in data["reports"]:
        assert "reportId" in report
        assert "categoryId" in report
        assert "location" in report
        if report["reportId"] == report_id:
            found = True
    
    assert found, f"Created report {report_id} not found in list"
    print(f"✓ Listed {len(data['reports'])} reports")

@pytest.mark.asyncio
async def test_get_report(client: AsyncClient):
    """Test getting a specific report."""
    # Create a report first
    create_response = await client.post(
        "/api/v1/reports/",
        json={
            "title": "Test Report for Get",
            "descriptionText": "Test description for getting",
            "categoryId": "infrastructure",
            "location": "Test Location",
            "isAnonymous": False,
            "attachments": []
        }
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["reportId"]
    
    # Get the report
    response = await client.get(f"/api/v1/reports/{report_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["reportId"] == report_id
    assert data["title"] == "Test Report for Get"
    
    print(f"✓ Retrieved report: {report_id}")

@pytest.mark.asyncio
async def test_update_report_status(client: AsyncClient):
    """Test updating report status."""
    # Create a report first
    create_response = await client.post(
        "/api/v1/reports/",
        json={
            "title": "Test Report for Update",
            "descriptionText": "Test description for updating",
            "categoryId": "infrastructure",
            "location": "Test Location",
            "isAnonymous": False,
            "attachments": []
        }
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["reportId"]
    
    # Update status
    payload = {
        "status": "Assigned",
        "notes": "Assigned to maintenance team"
    }
    
    response = await client.put(
        f"/api/v1/reports/{report_id}/status",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Assigned"
    assert data["reportId"] == report_id
    
    # Verify the change persisted
    check_response = await client.get(f"/api/v1/reports/{report_id}")
    check_data = check_response.json()
    assert check_data["status"] == "Assigned"
    
    print(f"✓ Updated report status: {report_id}")

@pytest.mark.asyncio
async def test_delete_report(client: AsyncClient):
    """Test deleting a report."""
    # Create a report first
    create_response = await client.post(
        "/api/v1/reports/",
        json={
            "title": "Test Report for Delete",
            "descriptionText": "Test description for deleting",
            "categoryId": "infrastructure",
            "location": "Test Location",
            "isAnonymous": False,
            "attachments": []
        }
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["reportId"]
    
    # Delete the report
    response = await client.delete(f"/api/v1/reports/{report_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = await client.get(f"/api/v1/reports/{report_id}")
    assert get_response.status_code == 404
    
    print(f"✓ Deleted report: {report_id}")