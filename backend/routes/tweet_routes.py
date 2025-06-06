from fastapi import FastAPI, HTTPException, Depends, Query, Path, APIRouter, Request
from typing import Optional, List
from sqlalchemy import func
from sqlalchemy.orm import Session
import sys
import os
from collections import defaultdict
import time
from backend.cachingsystem.cache import Cache
from backend.likebatcher.likebatcher import like_batcher, start_batcher

# Initializing cache functionality
cache = Cache()

# Start like batcher
start_batcher()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import database
from backend.models import Tweet, Hashtag, Media, Account
from backend.schemas import tweet, media, account, SearchRequest, TweetRead, HashtagRead
from backend.routes.account_routes import get_current_user
from sqlalchemy.orm import joinedload

router = APIRouter()

def get_db(request: Request):
    request.app.state.db_accesses += 1
    db = database.SessionLocal()
    try:
        yield db
    finally: 
        db.close()

@router.get("/")
def index(): 
    return {"name": "Homepage?"} #Maybe all tweets show up here idk

# Get all tweets
@router.get("/api/tweets", response_model=List[tweet.TweetRead])
def get_tweets(request: Request, q: Optional[str] = Query(None), db: Session = Depends(get_db)):
    request.app.state.logs.append(f"DB Access: method='{request.method}' Get all tweets")
    cache_key = f"tweets_{q}"
    cached_tweets = cache.get(cache_key)
    if cached_tweets:
        return cached_tweets
    # If not in cache, query the database
    query = db.query(Tweet).options(joinedload(Tweet.account))

    if q:
        query = query.filter(Tweet.content.ilike(f"%{q}%"))

    tweets = query.all()

    if not tweets:
        raise HTTPException(status_code=404, detail="No tweets found")

    # Cache the result
    cache.set(cache_key, tweets)
    return tweets


#Edit tweet
@router.put("/api/{account_id}/tweets/{tweet_id}", response_model=tweet.TweetRead)
def edit_tweets(request: Request, account_id: int, tweet_id: int, edit_tweet: tweet.TweetUpdate, db: Session = Depends(get_db), current_account: Account = Depends(get_current_user)):
    request.app.state.logs.append(f"DB Access: method='{request.method}' Edit tweet")
    tweet = db.query(Tweet).filter(Tweet.id == tweet_id, Tweet.account_id == account_id).first()

    if current_account.id != account_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to edit tweets on this account"
        )

    tweet = (
        db.query(Tweet)
            .filter(Tweet.id == tweet_id, Tweet.account_id == account_id)
            .first()
    )
    if not tweet:
        raise HTTPException(status_code=404, detail="The tweet you wanted to update was not found")
    
    # Updates text
    if edit_tweet.content is not None:
        tweet.content = edit_tweet.content

    # Updates hashtags
    if edit_tweet.hashtags is not None: 
        tweet.hashtags.clear()

        for tag in edit_tweet.hashtags:
            hashtag = db.query(Hashtag).filter(Hashtag.tag == tag).first()

            if not hashtag:
                hashtag = Hashtag(tag=tag)
                db.add(hashtag)
            tweet.hashtags.append(hashtag)

    # Update media
    if edit_tweet.media is not None:
        
        for m in tweet.media:
            db.delete(m)
        db.flush()

        tweet.media.clear()

        for url in edit_tweet.media:
            new_media = Media(url=url, media_type="image", tweet=tweet)
            db.add(new_media)

    db.commit()
    db.refresh(tweet)

    return tweet

# Delete tweet
@router.delete("/api/{account_id}/tweets/{tweet_id}")
def delete_tweets(request: Request, account_id: int, tweet_id: int, db: Session = Depends(get_db), current_account: Account = Depends(get_current_user)):
    request.app.state.logs.append(f"DB Access: method='{request.method}' Delete tweet")
    if current_account.id != account_id:
        raise HTTPException(status_code=403, detail="You don't have access to post, edit, or delete tweets on this account")
    
    tweet = db.query(Tweet).filter(Tweet.id == tweet_id, Tweet.account_id == account_id).first()

    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    
    db.delete(tweet)
    db.commit()

    return {"message": "Tweet Deleted"}

# Search based on hashtags
@router.post("/api/hashtags/search", response_model=List[HashtagRead])
def search_hashtags(search: SearchRequest, db: Session = Depends(get_db), request: Request = None):
    request.app.state.logs.append(f"DB Access: Search hashtags with query '{search.query}'")
    hashtags = db.query(Hashtag).filter(Hashtag.tag.ilike(f"%{search.query}%")).all()
    return hashtags

@router.post("/api/tweets/search", response_model=List[TweetRead])
def search_tweets(search: SearchRequest, db: Session = Depends(get_db), request: Request = None):
    request.app.state.logs.append(f"DB Access: Search tweets with query '{search.query}'")
    tweets = db.query(Tweet).options(joinedload(Tweet.account)).filter(Tweet.content.ilike(f"%{search.query}%")).all()
    return tweets

@router.post("/api/tweets/{tweet_id}/like")
def like_tweet(request: Request, tweet_id: int, db: Session = Depends(get_db)):
    request.app.state.logs.append(f"DB Access: method='{request.method}' Like tweet")
    current_time = time.time()
    if tweet_id in like_batcher:
        like_batcher[tweet_id]["likes"] += 1
        like_batcher[tweet_id]["time"] = current_time
    else:
        like_batcher[tweet_id] = {"likes": 1, "time": current_time}

    # Check if batch should be sent to the database
    if like_batcher[tweet_id]["likes"] > 10 or (current_time - like_batcher[tweet_id]["time"] > 60):
        tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()
        if not tweet:
            raise HTTPException(status_code=404, detail="Tweet not found")
        tweet.likes = (tweet.likes or 0) + like_batcher[tweet_id]["likes"]
        db.commit()
        del like_batcher[tweet_id]

    return {"message": "Like added"}

@router.post("/api/tweets", response_model=tweet.TweetRead)
def create_tweet(
    tweet_data: tweet.TweetCreate,
    db: Session = Depends(get_db),
    request: Request = None,
    current_account: Account = Depends(get_current_user)
):
    request.app.state.logs.append(f"DB Access: method='{request.method}' Post tweet")
    # Create new Tweet instance
    new_tweet = Tweet(
        content=tweet_data.content,
        account_id=current_account.id
    )
    db.add(new_tweet)
    db.flush()  # Get new_tweet.id before committing

    # Handle hashtags
    if tweet_data.hashtags:
        for tag in tweet_data.hashtags:
            hashtag = db.query(Hashtag).filter(Hashtag.tag == tag).first()
            if not hashtag:
                hashtag = Hashtag(tag=tag)
                db.add(hashtag)
            new_tweet.hashtags.append(hashtag)

    # Handle media
    if tweet_data.media:
        for url in tweet_data.media:
            new_media = Media(url=url, media_type="image", tweet=new_tweet)
            db.add(new_media)

    db.commit()
    db.refresh(new_tweet)
    return new_tweet