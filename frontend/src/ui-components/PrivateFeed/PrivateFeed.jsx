import styles from './PrivateFeed.module.css';
import { Link, useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getAccountByUsername, deleteTweet, editTweet, getCurrentUser } from '../../services/api';

// Utility to extract hashtags from text content
const extractHashtags = (text) =>
  text.match(/#[a-zA-Z0-9_]+/g)?.map(tag => tag.slice(1)) || [];

export default function PrivateFeed() {
  const { username } = useParams();
  const [account, setAccount] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [sortedTweets, setSortedTweets] = useState([]);

  // Track which tweet is being edited and draft content
  const [editing, setEditing] = useState({ id: null, content: '' });

  useEffect(() => {
    if (!username) return;

    // get the current user
    getCurrentUser()
      .then(user => setCurrentUser(user))
      .catch(() => setCurrentUser(null));

    // Fetch account data by username
    getAccountByUsername(username)
      .then(data => {
        setAccount(data);
        const tweetsWithTime = (data.tweets || []).map(tweet => ({
          ...tweet,
          fakeHoursAgo: Math.floor(Math.random() * 10),
        }));
        setSortedTweets(
          tweetsWithTime.sort((a, b) => a.fakeHoursAgo - b.fakeHoursAgo)
        );
      })
      .catch(err => console.error('Error fetching account:', err));
  }, [username]);

  const isOwner = currentUser?.id === account?.id;

  const startEdit = (tweet) => {
    setEditing({ id: tweet.id, content: tweet.content });
  };

  const cancelEdit = () => {
    setEditing({ id: null, content: '' });
  };

  const saveEdit = async (tweet) => {
    try {
      const newHashtags = extractHashtags(editing.content);
      const updated = await editTweet(account.id, tweet.id, {
        content: editing.content,
        hashtags: newHashtags,
        media: [],
      });

      setSortedTweets(prev =>
        prev.map(t =>
          t.id === tweet.id
            ? { ...t, content: updated.content, hashtags: newHashtags }
            : t
        )
      );
      cancelEdit();
    } catch (err) {
      console.error('Error editing tweet:', err);
      alert('Failed to edit tweet. You might not have permission.');
    }
  };

  const handleDelete = async (accountId, tweetId) => {
    try {
      await deleteTweet(accountId, tweetId);
      setSortedTweets(prev => prev.filter(tweet => tweet.id !== tweetId));
    } catch (err) {
      console.error('Error deleting tweet:', err);
      alert('Failed to delete tweet. You might not have permission.');
    }
  };

  if (!account) return <p>Loading...</p>;

  return (
    <div className={styles.feed}>
      <div className={styles.feed__profile}>
        <div className={styles.feed__profile__top}>
          <Link className={styles.feed__profile__top__arrow} to="/">&larr;</Link>
          <div className={styles.feed__profile__top__name}>
            <h2>{account.username}</h2>
            <p>{account.tweets ? account.tweets.length : 0} posts</p>
          </div>
        </div>

        <div className={styles.feed__profile__middle}>
          <img
            src="../../../public/placeholder1.jpg"
            alt="coverpic"
            className={styles.feed__profile__middle__coverimg}
          />
          <div className={styles.feed__profile__middle__profileimg}>
            <img
              src="../../../public/pepefrog.jpg"
              alt="profilepic"
              className={styles.feed__profile__middle__profileimg__img}
            />
          </div>
        </div>

        <div className={styles.feed__profile__bio}>
          <h2 className={styles.feed__profile__bio__name}>{account.username}</h2>
          <p className={styles.feed__profile__bio__handle}>@{account.handle}</p>
          <p className={styles.feed__profile__bio__text}>I like turdals</p>
          <ul className={styles.feed__profile__bio__info}>
            <li className={styles.feed__profile__bio__info__item}>Country</li>
            <li className={styles.feed__profile__bio__info__item}>Birth date</li>
            <li className={styles.feed__profile__bio__info__item}>
              {new Date(account.created_at).toLocaleDateString()}
            </li>
          </ul>
        </div>
      </div>

      <div className={styles.feed__tweet}>
        <div className={styles.feed__tweet__options}>
          <button className={styles.feed__tweet__options__button}>Posts</button>
          <button className={styles.feed__tweet__options__button}>Media</button>
        </div>

        {sortedTweets.map(tweet => (
          <div key={tweet.id} className={styles.feed__tweet__user}>
            <img
              src="../../../public/pepefrog.jpg"
              alt="profilepic"
              className={styles.feed__tweet__user__img}
            />
            <div className={styles.feed__tweet__user__info}>
              <div className={styles.feed__tweet__layout}>
                <Link
                  to={`/${account.username}/profile`}
                  className={styles.feed__tweet__user__info__name}
                >
                  {account.username}
                </Link>
                <p className={styles.feed__tweet__user__info__handle}>@{account.handle}</p>
                <p className={styles.feed__tweet__user__info__timestamp}>- {tweet.fakeHoursAgo}h</p>

                {isOwner && (
                  <div className={styles.feed__tweet__layout__girth}>
                      <button
                      className={styles.feed__tweet__layout__girth__delete}
                      onClick={() => handleDelete(account.id, tweet.id)}
                      title="Delete tweet"
                    >
                      &#x1F5D1;
                    </button>

                    {editing.id === tweet.id ? (
                      <> 
                        <button className={styles.feed__tweet__layout__girth__edit__buttones} onClick={() => saveEdit(tweet)}>Save</button>
                        <button className={styles.feed__tweet__layout__girth__edit__buttones} onClick={cancelEdit}>Cancel</button>
                      </>
                    ) : (
                      <button className={styles.feed__tweet__layout__girth__edit} onClick={() => startEdit(tweet)}>Edit</button>
                    )}
                  </div>
                )}
              </div>

              {editing.id === tweet.id ? (
                <textarea
                  className={styles.feed__tweet__layout__girth__edit__textarea}
                  value={editing.content}
                  onChange={e => setEditing(ed => ({ ...ed, content: e.target.value }))}
                />
              ) : (
                <p className={styles.feed__tweet__user__post}>{tweet.content}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
