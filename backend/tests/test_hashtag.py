import os 
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "testsecret"
#DATABASE_URL = os.getenv("DATABASE_URL")

from unittest.mock import MagicMock
import pytest 
from fastapi.testclient import TestClient

from backend.main import app 
from backend.routes.tweet_routes import get_db 
from backend.models import Hashtag, Account

client = TestClient(app)

@pytest.fixture(scope="module")
def mock_db():
    # Create a mock db session
    mock_session = MagicMock()

    # Define mock return values 
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query 

    # Simulate data
    mock_hashtag1 = MagicMock()
    mock_hashtag1.tag = "funny"

    mock_hashtag2 = MagicMock()
    mock_hashtag2.tag = "memes"

    mock_hashtag3 = MagicMock()
    mock_hashtag3.tag = "testing"

    mock_query.filter.return_value.all.return_value = [
        mock_hashtag1, mock_hashtag2, mock_hashtag3
    ]

    yield mock_session

@pytest.fixture(autouse=True)
def override_dependency(mock_db):
    # Reset the mock state before each test
    mock_db.reset_mock()

    def get_mock_db():
        yield mock_db
    app.dependency_overrides[get_db] = get_mock_db

def test_search_hashtags_found():
    response = client.post("/api/hashtags/search", json={"query": "fun"})
    assert response.status_code == 200
    data = response.json()
    assert any("funny" == h["tag"] for h in data)

# Simulates no hashtags found
def test_search_hashtags_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.all.return_value = []

    response = client.post("/api/hashtags/search", json={"query": "nonexistent"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No hashtags found"}