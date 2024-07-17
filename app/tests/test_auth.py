TEST_USER_USERNAME = "testuser"
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpassword"
TEST_USER_AUTH_TOKEN = None


def test_create_user(create_test_db, test_client) -> None:
    """
    Test the user creation endpoint.

    This test ensures that a user can be created via the registration endpoint and that the response contains
    the expected data.
    """

    response = test_client.post(
        "api/register/",
        json={"username": TEST_USER_USERNAME, "email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )

    # Verify response status code - 200 OK
    assert response.status_code == 200

    data = response.json()

    # Verify that the returned data contains provided username and email
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

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
    Test user creation enpoint in case, where provided username already exists.

    This test ensures that a user cannot be created with already occupied username, returning an error
    with 400 status code.
    """
    response = test_client.post(
        "api/register/",
        json={"username": "testuser", "email": "testuser2@example.com", "password": "testpassword"}
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
        data=dict(username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD)
    )

    # Verify response status code - 200 OK
    assert response.status_code == 200

    data = response.json()

    # Verify that response contains access_token and token_type fields
    assert "access_token" in data
    assert "token_type" in data

    # Save string with token for further testing
    global TEST_USER_AUTH_TOKEN
    TEST_USER_AUTH_TOKEN = f"{data['token_type']} {data['access_token']}"


def test_delete_user(create_test_db, test_client):
    """
    Test user deletion endpoint.

    This test ensures that user can be sucessfully deleted
    """
    response = test_client.delete(
        "api/profile",
        headers={
            "Authorization": TEST_USER_AUTH_TOKEN
        }
    )

    # Verify response status code - 200 OK
    assert response.status_code

    data = response.json()

    # Verify successfull deletion message
    assert data["message"] == f"User {TEST_USER_USERNAME} was deleted successfully"
