from .conftest import TestUserCredentials

user = TestUserCredentials()


def test_create_user(create_test_db, test_client) -> None:
    """
    Test the user creation endpoint.

    This test ensures that a user can be created via the registration endpoint and that the response contains
    the expected data.
    """

    response = test_client.post(
        "api/register/",
        json={"username": user.username, "email": user.email, "password": user.password}
    )

    # Verify response status code - 200 OK
    assert response.status_code == 200

    data = response.json()

    # Verify that the returned data contains provided username and email
    assert data["username"] == user.username
    assert data["email"] == user.email

    # Verify that response contains 'id' field, indicating successful user creation
    assert "id" in data

    # Send GET request to get profile of created user
    profile_response = test_client.get(
        f"api/profile/{data['id']}"
    )

    # Verify response status code - 200 OK
    assert profile_response.status_code == 200

    profile_data = profile_response.json()

    # Verify that created profile contains 'bio' field, indicating successful profile creation

    assert 'bio' in profile_data


def test_create_user_existing_username(create_test_db, test_client):
    """
    Test user creation endpoint in case, where provided username already exists.

    This test ensures that a user cannot be created with already occupied username, returning an error
    with 400 status code.
    """
    response = test_client.post(
        "api/register/",
        json={"username": user.username, "email": "testuser2@example.com", "password": user.password}
    )

    # Verify response status code - 400 BAD REQUEST
    assert response.status_code == 400
    data = response.json()

    # Verify error detail message
    assert data["detail"] == "Username already registered"


def test_login_user(create_test_db, test_client) -> str:
    """
    Test user login endpoint.

    This test ensures that user can be successfully logged in after creating an account.
    :return: JWT access token
    """

    # Send POST request with form-data containing user username and password
    response = test_client.post(
        "api/login/",
        data=dict(username=user.username, password=user.password)
    )

    # Verify response status code - 200 OK
    assert response.status_code == 200

    data = response.json()

    # Verify that response contains access_token and token_type fields
    assert "access_token" in data
    assert "token_type" in data

    # Save string with token for further testing
    user.access_token = f"{data['token_type']} {data['access_token']}"


def test_refresh_access_token(create_test_db, test_client):
    """
    Test updating access token enpoint.

    This test verifies, that with given access token a new access token can be retrieved.
    """
    response = test_client.get(
        "api/refresh-access-token",
        headers={
            "Authorization": user.access_token
        }
    )
    # Verify response status code - 200 OK
    assert response.status_code == 200

    data = response.json()

    # Verify that response contains new access token
    assert "access_token" in data
    assert "token_type" in data

    # Save new access token


def test_my_profile(create_test_db, test_client):
    """Test getting current user profile endpoint.

    This test ensures that user profile can be retrieved with provided credentials."""
    response = test_client.get(
        "api/my-profile",
        headers={"Authorization": user.access_token}
    )
    assert response.status_code == 200

    data = response.json()
    assert "bio" in data


def test_delete_user(create_test_db, test_client):
    """
    Test user deletion endpoint.

    This test ensures that user can be successfully deleted
    """
    response = test_client.delete(
        "api/profile",
        headers={
            "Authorization": user.access_token
        }
    )

    # Verify response status code - 200 OK
    assert response.status_code == 200

    data = response.json()

    # Verify successful deletion message
    assert data["message"] == f"User {user.username} was deleted successfully"
