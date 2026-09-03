from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_static_index_is_reachable(client):
    # Arrange
    expected_title = "Mergington High School Activities"

    # Act
    response = client.get("/static/index.html")
    response_text = response.text

    # Assert
    assert response.status_code == 200
    assert f"<title>{expected_title}</title>" in response_text


def test_get_activities_returns_activity_details_and_participants(client):
    # Arrange
    expected_activity = activities["Chess Club"]

    # Act
    response = client.get("/activities")
    response_data = response.json()

    # Assert
    assert response.status_code == 200
    assert response_data["Chess Club"] == expected_activity
    assert response_data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 200
    assert response_data == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 404
    assert response_data == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participant_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 400
    assert response_data == {
        "detail": "Student is already signed up for this activity"
    }
    assert len(activities[activity_name]["participants"]) == original_participant_count


def test_signup_requires_email(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")
    response_data = response.json()

    # Assert
    assert response.status_code == 422
    assert response_data["detail"][0]["loc"] == ["query", "email"]


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 200
    assert response_data == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in activities[activity_name]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": "student@mergington.edu"},
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 404
    assert response_data == {"detail": "Activity not found"}


def test_unregister_rejects_non_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not.registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 404
    assert response_data == {
        "detail": "Student is not registered for this activity"
    }


def test_activity_names_with_spaces_are_supported(client):
    # Arrange
    activity_name = "Chess Club"
    email = "spaces.work@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
