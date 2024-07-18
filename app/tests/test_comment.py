from typing import Optional

from .test_auth import user
from .conftest import create_user, TestSecondUserCredentials

# Create another user for testing
user2 = TestSecondUserCredentials()

# Post id placeholder
POST_ID: Optional[int] = None


def test_create_comment(create_test_db, test_client):
    """
    Test the comment creation endpoint.

    This test creates two comments by two different users and ensures, that comment can be created by user.
    """

    # Create users first
    create_user(user)
    create_user(user2)

    # Create post
    post_response = test_client.post(
        "api/posts/",
        json={
            "title": "feel free to comment",
            "content": "thank you"
        },
        headers={
            "Authorization": user.access_token
        }
    )
    assert post_response.status_code == 201

    post_id = post_response.json()["id"]

    global POST_ID
    POST_ID = post_id

    first_user_response = test_client.post(
        f"api/posts/{post_id}/comments",
        json={
            "content": "I'm first!"
        },
        headers={
            "Authorization": user.access_token
        }
    )
    second_user_response = test_client.post(
        f"api/posts/{post_id}/comments",
        json={
            "content": "those damn bots are always first"
        },
        headers={
            "Authorization": user2.access_token
        }
    )
    assert first_user_response.status_code == 201
    assert second_user_response.status_code == 201

    first_comment_data = first_user_response.json()
    second_comment_data = second_user_response.json()

    # Verify that post contains corresponding content and author
    assert "content" in first_comment_data
    assert "content" in second_comment_data
    assert first_comment_data["owner_id"] == user.user_id
    assert second_comment_data["owner_id"] == user2.user_id


def test_create_harmful_comment(create_test_db, test_client):
    """Test the comment creation with harmful content"""
    global POST_ID
    response = test_client.post(
        f"api/posts/{POST_ID}/comments",
        json={
            "content": "I wish you get hit by a truck"
        },
        headers={
            "Authorization": user2.access_token
        }
    )
    assert response.status_code == 422


def test_create_comment_unauthenticated(create_test_db, test_client):
    """Test the comment creation endpoint in case, where no authentication credentials provided."""
    global POST_ID
    response = test_client.post(
        f"api/posts/{POST_ID}/comments",
        json={
            "content": "I'm anon"
        }
    )
    assert response.status_code == 401


def test_list_comments(create_test_db, test_client):
    """
    Test list comments endpoint.

    This test ensures, that list of comments can be retrieved.
    """
    global POST_ID
    response = test_client.get(
        f"api/posts/{POST_ID}/comments"
    )
    assert response.status_code == 200

    data = response.json()

    # Verify retrieving of two previously created comments
    assert len(data) == 2
    assert data[0]["content"] == "I'm first!"


def test_update_comment(create_test_db, test_client):
    """Test updating comment endpoint.

    This test ensures, that comments can be updated by its author."""
    global POST_ID
    response = test_client.put(
        f"api/posts/{POST_ID}/comments/1",
        json={
            "content": "Answer below, if you are bot yourself!"
        },
        headers={"Authorization": user.access_token}
    )
    assert response.status_code == 200

    data = response.json()

    assert data["content"] == "Answer below, if you are bot yourself!"


def test_update_comment_unauthenticated(create_test_db, test_client):
    """Test for update comment endpoint in case, where no credentials were provided"""
    global POST_ID
    response = test_client.put(
        f"api/posts/{POST_ID}/comments/1",
        json={
              "content": "so listen here you mo"
        }
    )
    assert response.status_code == 401


def test_update_comment_unauthorized(create_test_db, test_client):
    """Test for update comment endpoint, where current user is not author of the comment"""
    global POST_ID
    response = test_client.put(
        f"api/posts/{POST_ID}/comments/1",
        json={
            "content": "I'm the one who knocks"
        },
        headers={"Authorization": user2.access_token}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Comment can be updated only by its author."


def test_delete_comment(create_test_db, test_client):
    """Test for delete comment endpoint."""
    global POST_ID
    response = test_client.delete(
        f'api/posts/{POST_ID}/comments/1',
        headers={"Authorization": user.access_token}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Comment deleted successfully."
