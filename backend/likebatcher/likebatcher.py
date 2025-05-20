import time
import requests
from threading import Thread
from collections import defaultdict
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Tweet

LOGGER_URL = "http://logger:8001/log"

like_batcher = defaultdict(lambda: {"likes": 0, "time": time.time()})

def log_db_access(message):
    try:
        requests.post(LOGGER_URL, json={"message": f"DB Access: {message}"})
    except Exception as e:
        print(f"Failed to log to logger service: {e}")

def add_like(tweet_id: int):
    current_time = time.time()
    like_batcher[tweet_id]["likes"] += 1
    like_batcher[tweet_id]["time"] = current_time

def flush_likes():
    while True:
        current_time = time.time()
        with SessionLocal() as db:
            for tweet_id, data in list(like_batcher.items()):
                if data["likes"] > 10 or (current_time - data["time"] > 60):
                    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()
                    if tweet:
                        tweet.likes = (tweet.likes or 0) + data["likes"]
                        db.commit()
                        log_db_access(f"Flushed {data['likes']} likes to tweet {tweet_id}")
                    # Safely remove the key if it exists
                    like_batcher.pop(tweet_id, None)
        time.sleep(60)  # Check every minute

def start_batcher():
    thread = Thread(target=flush_likes, daemon=True)
    thread.start()

if __name__ == "__main__":
    start_batcher()
    print("Like batcher started and running...")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Like batcher stopped.")