# Test setup configuration

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..main import app
from ..database import get_db, Base


# Setting up a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./app/tests/db/test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the test database
Base.metadata.create_all(bind=engine)


# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# Define test user credentials
class TestUserCredentials:
    def __init__(self):
        self.username = "testuser"
        self.email = "testuser@example.com"
        self.password = "testpassword"

        self.access_token = f'Bearer {client.post("api/login/", data=dict(username=self.username, password=self.password)).json().get("access_token")}'
        self.user_id = None


class TestSecondUserCredentials:
    def __init__(self):
        self.username = "anotheruser"
        self.email = "anotheruser@example.com"
        self.password = "testpassword"

        self.access_token = f'Bearer {client.post("api/login/", data=dict(username=self.username, password=self.password)).json().get("access_token")}'
        self.user_id = None


def create_user(user: TestUserCredentials | TestSecondUserCredentials):
    """
    Create a test user and save access token and user_id to user object.

    """
    create_user_response = client.post(
        "api/register/",
        json={"username": user.username, "email": user.email, "password": user.password}
    )

    # Login to get access token
    login_user_response = client.post(
        "api/login/",
        data=dict(username=user.username, password=user.password)
    )

    login_user_data = login_user_response.json()

    # Save access token
    user.access_token = f'{login_user_data["token_type"]} {login_user_data["access_token"]}'

    # Create request to my-profile endpoint to get and save user_id
    my_profile_response = client.get(
        "api/my-profile",
        headers={"Authorization": user.access_token}
    )
    my_profile_data = my_profile_response.json()
    user_id = my_profile_data["user_id"]
    user.user_id = user_id


@pytest.fixture(scope="module")
def test_client():
    yield client
    Base.metadata.drop_all(bind=engine)


# Create database when launching tests
@pytest.fixture(scope="module")
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


