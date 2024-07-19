import datetime
from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy import text

from .test_auth import user
from .conftest import create_user, TestSecondUserCredentials

from .conftest import override_get_db

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
    response1 = test_client.delete(
        f'api/posts/{POST_ID}/comments/1',
        headers={"Authorization": user.access_token}
    )
    response2 = test_client.delete(
        f'api/posts/{POST_ID}/comments/2',
        headers={"Authorization": user2.access_token}
    )
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()["detail"] == "Comment deleted successfully."
    assert response2.json()["detail"] == "Comment deleted successfully."


def test_comments_daily_breakdown(create_test_db, test_client):
    """
    Test comment analytic endpoint.

    This test ensures, that for specified days range corresponding comments will be returned in proper format.
    """
    # Create some comments
    global POST_ID

    # Create comments in a loop
    for i in range(1, 5):
        last_comment_response = test_client.post(
            f'api/posts/{POST_ID}/comments',
            json={
                'content': f'Comment number {i}'
            },
            headers={"Authorization": user.access_token}
        )

    assert last_comment_response.status_code == 201

    # Create requests for test analytic endpoint

    # All comments for today
    today_date = datetime.today().strftime("%Y-%m-%d")
    comments_for_today_response = test_client.get(f'api/comments-daily-breakdown?date_from={today_date}&date_to={today_date}')
    assert comments_for_today_response.status_code == 200

    # Comments for range, including today
    two_days_before_date = (datetime.today() - timedelta(days=2)).strftime("%Y-%m-%d")
    two_days_after_date = (datetime.today() + timedelta(days=2)).strftime("%Y-%m-%d")
    comments_for_range_including_today = test_client.get(
        f'api/comments-daily-breakdown?date_from={two_days_before_date}&date_to={two_days_after_date}')
    assert comments_for_range_including_today.status_code == 200

    # Comments for days, where there weren't any comments (excluding today)
    four_days_after_date = (datetime.today() + timedelta(days=4)).strftime("%Y-%m-%d")

    comments_for_days_out_range_response = test_client.get(f'api/comments-daily-breakdown?date_from={two_days_after_date}&date_to={four_days_after_date}')
    assert comments_for_days_out_range_response.status_code == 200

    # Request with no dates specified
    comments_for_no_date_response = test_client.get(f'api/comments-daily-breakdown')
    assert comments_for_no_date_response.status_code == 422

    # Test response data

    # Verify amount of comments for all range of days counter
    assert comments_for_today_response.json().get("total_comments_amount") == 4

    # Verify comments items
    assert comments_for_range_including_today.json().get("comments").get(today_date).get("items")[0].get("content") == "Comment number 1"
    assert comments_for_range_including_today.json().get("comments").get(today_date).get("items")[0].get("owner_id") == 1

    # Verify amount of comments for one day counter
    assert comments_for_range_including_today.json().get("comments").get(today_date).get("comments_amount") == 4

    # Verify that no comments were returned with dates out of range
    assert comments_for_days_out_range_response.json().get("total_comments_amount") == 0
