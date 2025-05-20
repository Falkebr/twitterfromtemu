import os 
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "testsecret"

import time 
import pytest
import threading
from unittest.mock import patch, MagicMock

from backend.likebatcher.likebatcher import like_batcher, add_like, flush_likes, start_batcher
from backend.models import Tweet

# Fixtures to reduce repetition
## Should clear the like_batcher dict before each test for a clean slate
@pytest.fixture(autouse=True)
def clear_like_batcher():
    like_batcher.clear()

## Should create a mock Tweet object with preset id and likes
@pytest.fixture 
def mock_tweet():
    tweet = MagicMock(spec=Tweet)
    tweet.id = 10
    tweet.likes = 5
    return tweet 

## Should create a mock database session that returns the mock Tweet when queried
@pytest.fixture
def mock_db_with_tweet(mock_tweet):
    mock_db = MagicMock()
    # Mocking the query chain to return the tweet
    mock_db.query.return_value.filter.return_value.first.return_value = mock_tweet
    return mock_db

# Unit tests
## Test add_like correctly increments likes and updates tmestamp for a tweet
def test_add_like_updates_like_batcher():
    tweet_id = 10
    add_like(tweet_id)
    assert like_batcher[tweet_id]["likes"] == 1

    # Adding some more to check if incrementing works
    add_like(tweet_id)
    assert like_batcher[tweet_id]["likes"] == 2

    # Checks that the timestamp is recent (within 1 second)
    assert abs(like_batcher[tweet_id]["time"] - time.time()) < 1

## Tests that flush_likes properly flushes batched likes to the db, commits, logs, and clears the batch
@patch("backend.likebatcher.likebatcher.log_db_access")
@patch("backend.likebatcher.likebatcher.SessionLocal")
@patch("backend.likebatcher.likebatcher.time.sleep", side_effect=InterruptedError)
def test_flush_likes_flushes_and_clears_batch(mock_sleep, mock_sessionlocal, mock_log):
    tweet_id = 29
    mock_tweet = MagicMock()
    mock_tweet.id = tweet_id
    mock_tweet.likes = 2

    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = mock_tweet
    mock_sessionlocal.return_value.__enter__.return_value = db_mock

    # Add 12 likes older than 60 seconds to trigger flush
    like_batcher[tweet_id] = {"likes": 12, "time": time.time() - 100}

    # Run flush_likes, which will be interrupted after one iteration
    with pytest.raises(InterruptedError):
        flush_likes()

    # Validate likes updated, commit called, log called, and batch cleared
    assert mock_tweet.likes == 14
    db_mock.commit.assert_called_once()
    mock_log.assert_called_once_with(f"Flushed 12 likes to tweet {tweet_id}")
    assert tweet_id not in like_batcher

## Tests that start_batcher starts a daemon thread running flush_likes
def test_start_batcher_starts_daemon_thread():
    # Stub flush_likes with an infinite loop to keep the thread alive
    def block_forever():
        while True:
            time.sleep(1)

    with patch("backend.likebatcher.likebatcher.flush_likes", side_effect=block_forever):
        start_batcher()

        # Wait a moment for thread to start
        time.sleep(0.1)

        # Find all non-main threads
        threads = [t for t in threading.enumerate() if t.name != "MainThread"]
        assert len(threads) > 0, "No additional thread started"

        flush_thread = threads[0]
        assert flush_thread.is_alive(), "Thread is dead"
        assert flush_thread.daemon, "Thread is not daemon"