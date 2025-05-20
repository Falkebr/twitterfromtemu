import os 
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "testsecret"

import pytest 
from unittest.mock import MagicMock
from fastapi import HTTPException
from jose import jwt

from backend.auth import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM, auth_user, get_current_user
from backend.models import Account

# Fixtures to reduce repetition
## Should create mock user with hashed password
@pytest.fixture
def mock_user():
    user = MagicMock(spec=Account)
    user.username = "testuser"
    user.password = hash_password("fantasticPassword321")
    return user

## Should create mock db that returns the mock user on query
@pytest.fixture
def mock_db_with_user(mock_user):
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = mock_user
    return mock_db

# Unit tests
## Should hash a password and verify it correctly
def test_hash_and_verify_password():
    password = "donotguessmypassword109"
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert verify_password(password, hashed) is True
    assert verify_password("somewrongpassword", hashed) is False

## Should create a valid access token with correct payload
def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert isinstance(token, str)

    # Decode token to verify content
    payload = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload

## Should return user if username and password is correct
def test_auth_user_success(mock_db_with_user, mock_user):
    result = auth_user(mock_db_with_user, mock_user.username, "fantasticPassword321")
    assert result == mock_user 

## Should return None if password is incorrect
def test_auth_user_wrong_password(mock_db_with_user, mock_user):
    result = auth_user(mock_db_with_user, mock_user.username, "wrongPassword")
    assert result is None

## Should return None if user does not exist
def test_auth_user_user_not_found():
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None

    result = auth_user(mock_db, "doesntexist", "redactedpassword")
    assert result is None 

## Should return user if token is valid and user exists
def test_get_current_user_success(mock_db_with_user, mock_user):
    token_data = {"sub": mock_user.username}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    user = get_current_user(db=mock_db_with_user, token=token)
    assert user == mock_user

## Should raise HTTPException if token is invalid
def test_get_current_user_invalid_token():
    bad_token = "not.a.good.token.apparently"
    mock_db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db, token=bad_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"

## Should raise HTTPException if token is missing "sub" field
def test_get_current_user_missing_sub():
    token = jwt.encode({}, SECRET_KEY, algorithm=ALGORITHM)
    mock_db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db, token=token)

    assert exc_info.value.status_code == 401

## Should raise HTTPException if user from token is not found in db
def test_get_current_user_user_not_found():
    token = jwt.encode({"sub": "userthatdontexist"}, SECRET_KEY, algorithm=ALGORITHM)
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=mock_db, token=token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"