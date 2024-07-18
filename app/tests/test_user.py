from .test_auth import user
from .conftest import create_user


def test_get_user_profile(create_test_db, test_client):
    """
    Test the user profile endpoint.

    This test ensures that a user's profile can be retrieved by their ID.
    """
    # Create user first
    create_user(user)

    # Test getting the user profile by id
    response = test_client.get(
        f"api/profile/{user.user_id}"
    )
    assert response.status_code == 200

    profile_data = response.json()
    assert profile_data["user_id"] == user.user_id
    assert "bio" in profile_data
