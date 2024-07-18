from .test_auth import user
from .conftest import create_user, TestSecondUserCredentials

# Create another user for testing
user2 = TestSecondUserCredentials()


def test_create_post(create_test_db, test_client):
    """
    Test the post creation endpoint.

    This test creates two posts by two different users and ensures, that post can be created by user.
    """

    # Create users first
    create_user(user)
    create_user(user2)

    first_user_response = test_client.post(
        "api/posts",
        json={
            "title": "test title",
            "content": "test content"
        },
        headers={
            "Authorization": user.access_token
        }
    )
    second_user_response = test_client.post(
        "api/posts",
        json={
            "title": "another test title",
            "content": "another test content"
        },
        headers={
            "Authorization": user2.access_token
        }
    )
    assert first_user_response.status_code == 201
    assert second_user_response.status_code == 201

    first_post_data = first_user_response.json()
    second_post_data = second_user_response.json()

    # Verify that post contains corresponding content and author
    assert "content" in first_post_data
    assert "content" in second_post_data
    assert first_post_data["owner_id"] == user.user_id
    assert second_post_data["owner_id"] == user2.user_id


def test_create_post_unauthenticated(create_test_db, test_client):
    """Test the post creation endpoint in case, where no authentication credentials provided."""
    response = test_client.post(
        "api/posts",
        json={
            "title": "test title",
            "content": "test content"
        }
    )
    assert response.status_code == 401


def test_list_posts(create_test_db, test_client):
    """
    Test list posts endpoint.

    This test ensures, that list of posts can be retrieved.
    """
    response = test_client.get(
        "api/posts"
    )
    assert response.status_code == 200

    data = response.json()

    # Verify retrieving of two previously created posts
    assert len(data) == 2
    assert data[0]["content"] == "test content"


def test_get_post(create_test_db, test_client):
    """
    Test get_post endpoint.

    This test ensures that a post can be retrieved by its id (In our case, id 1).
    """
    response = test_client.get(
        "api/posts/1"
    )
    assert response.status_code == 200

    data = response.json()

    assert data["content"] == "test content"


def test_update_post(create_test_db, test_client):
    """Test updating post endpoint.

    This test ensures, that post can be updated by its author."""
    response = test_client.put(
        "api/posts/1",
        json={
            "title": "test title",
              "content": "updated content"
        },
        headers={"Authorization": user.access_token}
    )
    assert response.status_code == 200

    data = response.json()

    assert data["content"] == "updated content"


def test_update_post_unauthenticated(create_test_db, test_client):
    """Test for update post endpoint in case, where no credentials were provided"""
    response = test_client.put(
        "api/posts/1",
        json={
            "title": "test title",
              "content": "updated content"
        }
    )
    assert response.status_code == 401


def test_update_post_unauthorized(create_test_db, test_client):
    """Test for update post endpoint, where current user is not author of the post"""
    response = test_client.put(
        "api/posts/1",
        json={
            "title": "test title",
              "content": "updated content"
        },
        headers={"Authorization": user2.access_token}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Post can be updated only by its author."


def test_delete_post(create_test_db, test_client):
    """Test for delete post endpoint."""
    response = test_client.delete(
        'api/posts/1',
        headers={"Authorization": user.access_token}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Post deleted successfully."
