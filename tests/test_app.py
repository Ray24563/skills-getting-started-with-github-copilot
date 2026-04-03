"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data before each test to ensure isolation"""
    # Store original data
    original_activities = activities.copy()

    # Reset to initial state
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })

    yield

    # Restore original data after test
    activities.clear()
    activities.update(original_activities)


def test_root_redirect(client):
    """Test that GET / redirects to the static index page"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"


def test_get_activities(client):
    """Test GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 3  # Three activities

    # Check that Chess Club is present with expected structure
    assert "Chess Club" in data
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)
    assert len(chess_club["participants"]) == 2


def test_signup_for_activity_success(client):
    """Test successful signup for an existing activity"""
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Get initial participant count
    initial_response = client.get("/activities")
    initial_participants = len(initial_response.json()[activity_name]["participants"])

    # Sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]

    # Verify participant was added
    final_response = client.get("/activities")
    final_participants = final_response.json()[activity_name]["participants"]
    assert len(final_participants) == initial_participants + 1
    assert email in final_participants


def test_signup_for_nonexistent_activity(client):
    """Test signup for a non-existent activity returns 404"""
    activity_name = "NonExistent Club"
    email = "student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_activity_data_structure(client):
    """Test that activity data has the correct structure"""
    response = client.get("/activities")
    data = response.json()

    for activity_name, activity_data in data.items():
        assert isinstance(activity_data, dict)
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for field in required_fields:
            assert field in activity_data

        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)

        # All participants should be email strings
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant  # Basic email validation