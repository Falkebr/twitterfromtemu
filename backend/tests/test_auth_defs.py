import os 
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "testsecret"

from unittest.mock import MagicMock
import pytest 
from fastapi.testclient import TestClient
from jose import jwt

from backend.main import app 
from backend.routes.tweet_routes import get_db 
from backend.auth import hash_password, verify_password, create_access_token, ALGORITHM

# Unit test for hash_password and verify_password
def test_hash_and_verify_password():
    password = "donotguessmypassword109"
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert verify_password(password, hashed) is True
    assert verify_password("somewrongpassword", hashed) is False

# Unit test for create_access_token
def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert isinstance(token, str)

    # Decode token to verify content
    payload = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload
