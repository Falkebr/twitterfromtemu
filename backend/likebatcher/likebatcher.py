import time
from threading import Thread
from collections import defaultdict
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Tweet

like_batcher = defaultdict(lambda: {"likes": 0, "time": time.time()})

def add_like(tweet_id: int):
    current_time = time.time()
    like_batcher[tweet_id]["likes"] += 1
    like_batcher[tweet_id]["time"] = current_time

def flush_likes():
    while True:
        time.sleep(60)  # Check every minute
        current_time = time.time()
        with SessionLocal() as db:
            for tweet_id, data in list(like_batcher.items()):
                if data["likes"] > 10 or (current_time - data["time"] > 60):
                    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()
                    if tweet:
                        tweet.likes = (tweet.likes or 0) + data["likes"]
                        db.commit()
                    del like_batcher[tweet_id]

def start_batcher():
    thread = Thread(target=flush_likes, daemon=True)
    thread.start()