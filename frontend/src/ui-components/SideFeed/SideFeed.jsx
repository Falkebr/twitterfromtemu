import styles from './SideFeed.module.css';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import SearchBar from '../Search/SearchBar';
import { 
    searchAccounts, 
    searchHashtags, 
    searchTweets 
} from '../../services/api'; 

export default function SideFeed() {
  const [accounts, setAccounts] = useState([]);
  const [hashtags, setHashtags] = useState([]);
  const [tweets, setTweets]     = useState([]);

  const onSearch = async (q) => {
    // exactly like your original, but using the helpers:
    try {
      const accountsData = await searchAccounts(q);
      const hashtagsData = await searchHashtags(q);
      const tweetsData   = await searchTweets(q);

      setAccounts(Array.isArray(accountsData) ? accountsData : []);
      setHashtags(Array.isArray(hashtagsData) ? hashtagsData : []);
      setTweets(Array.isArray(tweetsData)     ? tweetsData     : []);
    } catch (err) {
      // this will only fire on non-404 errors
      console.error('Error during search:', err);
      // and we still fall through, but you might choose to:
      // setAccounts([]); setHashtags([]); setTweets([]);
    }
  };

    return (
        <div className={styles.SideFeed}>
            <SearchBar className={styles.SideFeed__search} onSearch={onSearch} />

            <div className={styles.SideFeed__card}>
                <h3 className={styles.SideFeed__card__header}>Search Results</h3>

                {/* Display matching accounts */}
                <div>
                    <h4>Accounts</h4>
                    {accounts.map((account) => (
                        <div key={account.username} className={styles.SideFeed__card__suggestions}>
                            <div>
                                <img
                                    src="../../../public/npcwojak.png"
                                    alt="profilepic"
                                    className={styles.SideFeed__card__suggestions__img}
                                />
                            </div>
                            <div>
                                <Link
                                    to={`/${account.username}/profile`}
                                    className={styles.SideFeed__card__suggestions__name}
                                >
                                    {account.username}
                                </Link>
                                <p className={styles.SideFeed__card__suggestions__handle}>@{account.handle}</p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Display matching hashtags */}
                <div>
                    <h4>Hashtags</h4>
                    {hashtags.map((hashtag) => (
                        <p key={hashtag.id} className={styles.SideFeed__card__suggestions__handle}>
                            #{hashtag.tag}
                        </p>
                    ))}
                </div>

                {/* Display matching tweets */}
                <div>
                    <h4>Tweets</h4>
                    {tweets.map((tweet) => (
                        <div key={tweet.id} className={styles.SideFeed__card__suggestions}>
                            <p>{tweet.content}</p>
                            <p className={styles.SideFeed__card__suggestions__handle}>
                                - @{tweet.account.username}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}