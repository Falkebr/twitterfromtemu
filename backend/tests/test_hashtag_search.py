import os 
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "testsecret"

from unittest.mock import MagicMock
import pytest 
from fastapi.testclient import TestClient

from backend.main import app 
from backend.routes.tweet_routes import get_db 

client = TestClient(app)

@pytest.fixture(scope="module")
def mock_db():
    # Create a mock db session
    mock_session = MagicMock()

    # Define mock return values 
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query 

    # Simulate data using a loop
    tags = ["funny", "memes", "testing"]
    mock_hashtags = []
    for tag in tags:
        mock_tag = MagicMock()
        mock_tag.tag = tag
        mock_hashtags.append(mock_tag)

    # Simulate filtering (make hashtags case-insensitive)
    def filter_side_effect(*args, **kwargs):
        m = MagicMock()

        def all_side_effect():
            q = getattr(mock_session, "query_string", "").strip()
            return [h for h in mock_hashtags if q.lower() in h.tag.lower()]

        m.all.side_effect = all_side_effect
        return m 

    mock_query.filter.side_effect = filter_side_effect

    yield mock_session

@pytest.fixture(autouse=True)
def override_dependency(mock_db):
    # Reset the mock state before each test
    mock_db.reset_mock()
    mock_db.query_string = ""

    def get_mock_db():
        yield mock_db
    app.dependency_overrides[get_db] = get_mock_db

# Positive test cases:
@pytest.mark.parametrize("query, expected", [
    ("fun", "funny"),
    ("mem", "memes"),
    ("test", "testing"),
])
def test_hashtags_found_variants(query, expected, mock_db):
    mock_db.query_string = query
    response = client.post("/api/hashtags/search", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert any(h["tag"] == expected for h in data)

# Negative test cases:
## Simulates no hashtags found
def test_hashtags_not_found(mock_db):
    mock_db.query_string = "nonexistent"
    response = client.post("/api/hashtags/search", json={"query": "nonexistent"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No hashtags found"}

# Edge cases 
## Positive cases: Case insensitivity when searching for hashtags
@pytest.mark.parametrize("query, expected", [
    ("FUN", "funny"),
    ("MEm", "memes"),
    ("tESt", "testing")
])

def test_search_hashtags_case_insensitive(query, expected, mock_db):
    mock_db.query_string = query
    response = client.post("/api/hashtags/search", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert any(h["tag"] == expected for h in data)

## Negative cases: Tests that you can't have no hashtag input, special characters, whitespaces, 1000 character long hashtag
@pytest.mark.parametrize("query", ["", "$@!#", "   ", "a" * 1000])
def test_hashtags_edge_cases_not_found(query, mock_db):
    mock_db.query_string = query
    response = client.post("/api/hashtags/search", json={"query": query})
    assert response.status_code == 404
    assert response.json() == {"detail": "No hashtags found"}