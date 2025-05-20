import sys 
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest 
from fastapi.testclient import TestClient

from backend.main import app 
from backend.database import SessionLocal, Base, engine
from backend.models import Hashtag
from backend.routes.tweet_routes import get_db 
from sqlalchemy.orm import Session

client = TestClient(app)

def override_get_db():
    try:
        db = SessionLocal()
        yield db 
    finally: 
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def test_db():
    # Create tables if needed
    Base.metadata.create_all(bind=engine)

    # Create a test database session and insert test data
    db = SessionLocal()

    # Some hashtags to search
    sample_tags = ["funny", "memes", "testing"]
    for tag in sample_tags:
        db.add(Hashtag(tag=tag))
    db.commit()

    yield db 

    # Delete test data / clean up
    db.query(Hashtag).filter(Hashtag.tag.in_(sample_tags)).delete(synchronize_session=False)
    db.commit()
    db.close()

def test_search_hashtags_found(test_db):
    response = client.post("/api/hashtags/search", json={"query": "fun"})
    assert response.status_code == 200
    data = response.json()
    assert any("funny" == h["tag"] for h in data)

def test_search_hashtags_not_found(test_db):
    response = client.post("/api/hashtags/search", json={"query": "nonexistent"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No hashtags found"}