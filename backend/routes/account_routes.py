from fastapi import FastAPI, HTTPException, Depends, Form, APIRouter, Request
from typing import List
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.auth import auth_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from datetime import timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from backend import database
from backend.models import Account, Tweet, Hashtag, Media
from backend.schemas.account import AccountRead, AccountCreate, AccountBase, AccountCredentials, SearchRequest
from backend.schemas.tweet import TweetRead, TweetCreate, TweetUpdate, TweetBase
from backend.schemas.media import MediaBase, MediaCreate, MediaRead
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("SECRET_KEY environment variable is not set.")
ALGORITHM = "HS256"

router = APIRouter()

# Hashing Passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Password Verification Function
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Database session dependency
def get_db(request: Request):
    request.app.state.db_accesses += 1
    db = database.SessionLocal()
    try:
        yield db
    finally: 
        db.close()

# Authenticate User (login by username)
def auth_user(db: Session, username: str, password: str):
    user = db.query(Account).filter(Account.username == username).first()
    if not user or not verify_password(password, user.password):
        return None
    return user

# JWT Authentication Dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/accounts/login")

# Function to get the current logged-in user from the token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        # Decode the JWT token to get user details
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch the user from the database
    user = db.query(Account).filter(Account.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Routes

# Create account
@router.post("/api/accounts", response_model=AccountRead)
def create_account(account: AccountCreate, db: Session = Depends(get_db), request: Request = None):
    request.app.state.logs.append(f"DB Access: method='{request.method}' Create account")
    hashed_pw = hash_password(account.password)

    new_account = Account(
        username=account.username,
        email=account.email,
        handle=account.handle,
        password=hashed_pw 
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

# Login with username
@router.post("/api/accounts/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    request.app.state.logs.append(f"DB Access: method='{request.method}' Login")
    user = auth_user(db, username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Get all accounts
@router.get("/api/accounts")
def get_all_accounts(db: Session = Depends(get_db), request: Request = None):
    request.app.state.logs.append(f"DB Access: method='{request.method}' Fetch all accounts")
    accounts = db.query(Account).all()
    return [
        {
            "id": account.id,
            "username": account.username,
            "handle": account.handle,
            "email": account.email,
            "created_at": account.created_at.isoformat(),
            "tweets": [tweet.to_dict() for tweet in account.tweets]  # Use to_dict() for tweets
        }
        for account in accounts
    ]

# Search accounts
@router.post("/api/accounts/search", response_model=List[AccountRead])
def search_accounts(request: SearchRequest, db: Session = Depends(get_db), req: Request = None):
    req.app.state.logs.append(f"DB Access: Search accounts with query '{request.query}'")
    accounts = db.query(Account).filter(
        Account.username.ilike(f"%{request.query}%") | Account.email.ilike(f"%{request.query}%")
    ).all()
    return accounts

# Get current logged-in user's data
@router.get("/api/accounts/me", response_model=AccountRead)
def get_current_account(current_user: Account = Depends(get_current_user), db: Session = Depends(get_db), request: Request = None):
    request.app.state.logs.append(f"DB Access: method='{request.method}' Fetch current user's account")
    user = db.query(Account).filter(Account.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Get account by username
@router.get("/api/accounts/{username}", response_model=AccountRead)
def get_account(username: str, db: Session = Depends(get_db), request: Request = None):
    request.app.state.logs.append(f"DB Access: method='{request.method}' Fetch account with username '{username}'")
    account = db.query(Account).filter(Account.username == username).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    response = {
        "id": account.id,
        "username": account.username,
        "email": account.email,
        "handle": account.handle,
        "created_at": account.created_at.isoformat(),
        "tweets": [
            {
                **tweet.to_dict(),
                "account": {
                    "id": account.id,  # Only include the account ID
                },
                "hashtags": [hashtag.to_dict() for hashtag in tweet.hashtags],
                "media": [media.to_dict() for media in tweet.media],
            }
            for tweet in account.tweets
        ],
    }
    return response