import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

BASE_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(BASE_ACTIVITIES))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def activity_signup_url(activity_name: str) -> str:
    return f"/activities/{quote(activity_name)}/signup"


def activity_remove_url(activity_name: str) -> str:
    return f"/activities/{quote(activity_name)}/participants"


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert expected_activity in body
    assert body[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(activity_signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(activity_signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_student(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(activity_remove_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(activity_remove_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_activity_not_found_returns_404_for_signup(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "test@mergington.edu"

    # Act
    response = client.post(activity_signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_activity_not_found_returns_404_for_remove(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "test@mergington.edu"

    # Act
    response = client.delete(activity_remove_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
