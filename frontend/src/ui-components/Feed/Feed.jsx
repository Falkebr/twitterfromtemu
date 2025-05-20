import styles from './Feed.module.css';
import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import {
    getCurrentUser,
    getAccounts,
    postTweet,
    likeTweet
} from '../../services/api'; 

export default function Feed() {
    const [accounts, setAccounts] = useState([]);
    const [allTweets, setAllTweets] = useState([]);
    const [tweetPost, setTweetPost] = useState('');
    const [user, setUser] = useState(null);

  useEffect(() => {
    // load current user (if logged in)
    getCurrentUser()
      .then(setUser)
      .catch(() => { /* no-op if not authenticated */ });

    // load all accounts + their tweets
    getAccounts()
      .then(accounts => {
        const tweets = accounts
          .flatMap(account =>
            (account.tweets || []).map(tweet => ({
              ...tweet,
              accountUsername: account.username,
              accountHandle:   account.handle,
              created_at:      tweet.created_at,
            }))
          )
          .sort((a, b) => b.created_at - a.created_at);
        setAllTweets(tweets);
      })
      .catch(err => console.error('Error fetching accounts:', err));
  }, []);  

  const handleTweetSubmit = async (e) => {
    e.preventDefault();
    if (!user || !tweetPost.trim()) return;

    const hashtagList = tweetPost
      .match(/#[a-zA-Z0-9_]+/g)
      ?.map(tag => tag.slice(1)) || [];

    try {
      const newTweet = await postTweet({
        content:  tweetPost,
        hashtags: hashtagList,
        media:    [],
      });

      setAllTweets(prev => [{
        ...newTweet,
        accountUsername: user.username,
        accountHandle:   user.handle,
        created_at:      newTweet.created_at,
      }, ...prev]);

      setTweetPost('');
    } catch (err) {
      console.error('Error posting tweet:', err);
    }
  };

  const handleLike = async (tweetId) => {
    if (!user) return;

    try {
      const updatedTweet = await likeTweet(tweetId);
      setAllTweets(prev =>
        prev.map(t =>
          t.id === updatedTweet.id
            ? { ...t, likes: updatedTweet.likes }
            : t
        )
      );
    } catch (err) {
      console.error('Error liking tweet:', err);
    }
  };

  const formatRelativeTime = (timestamp) => {
    if (!timestamp) return 'just now';
    const diff = (Date.now() - timestamp) / 1000;
    if (diff < 60)    return `${Math.floor(diff)}s`;
    if (diff < 3600)  return `${Math.floor(diff / 60)}m`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
    return `${Math.floor(diff / 86400)}d`;
  };

    return (
        <div className={styles.feed}>
            {/* Post Tweet Section */}
            <div className={styles.feed__post}>
                <img 
                    src="../../../public/pepefrog.jpg" 
                    alt=""
                    className={styles.feed__post__img}
                />
                <form className={styles.feed__post__form}
                    method="post"
                    encType="multipart/form-data"
                    onSubmit={handleTweetSubmit}
                >
                    <textarea 
                        name="tweet" 
                        id="tweet_textfield"
                        className={styles.feed__post__form__input}
                        placeholder='Post propaganda and fake news'
                        value={tweetPost}
                        onChange={(e) => setTweetPost(e.target.value)}
                    ></textarea>
                    <div className={styles.feed__post__form__input__append}>
                        <label>
                            📷
                            <input type="file" name="image" accept="image/*" hidden />
                        </label>
                        <label>
                            🎵
                            <input type="file" name="audio" accept="audio/*" hidden />
                        </label>
                        <label>
                            🎥
                            <input type="file" name="video" accept="video/*" hidden />
                        </label>

                        <button type="submit" className={`${styles.feed__post__form__input__append__post} button`}>Post</button>
                    </div>
                </form>
            </div>

            {/* Display Tweets */}
            <div>
                <div className={styles.feed__tweet}>
                    {allTweets.map((tweet, index) => (
                        <div key={index} className={styles.feed__tweet__user}>
                            <div>
                                <img 
                                    src="../../../public/npcwojak.png" alt="profilepic"
                                    className={styles.feed__tweet__user__img} 
                                />
                            </div>
                            <div className={styles.feed__tweet__user__info}>
                                <div className={styles.feed__tweet__layout}>
                                    <Link 
                                        to={`/${tweet.accountUsername}/profile`}
                                        className={styles.feed__tweet__user__info__name}
                                    >
                                        {tweet.accountUsername}
                                    </Link>
                                    <p className={styles.feed__tweet__user__info__handle}>@{tweet.accountHandle}</p>
                                    <p className={styles.feed__tweet__user__info__timestamp}>- {formatRelativeTime(tweet.created_at)}</p>
                                </div>
                                <div>
                                    <p className={styles.feed__tweet__user__post}>{tweet.content}</p>
                                </div>
                                <div>
                                    <button onClick={() => handleLike(tweet.id)} className={styles.feed__tweet__like_button}>Like</button>
                                    <span>{tweet.likes || 0} Likes</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}