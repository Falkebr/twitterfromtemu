const BASE_BACKEND_URL = 'http://localhost';
const API_ROOT = `${BASE_BACKEND_URL}/api`;	

// This function is used to make API requests to the backend server.
async function request(path, {
  method    = 'GET',
  body      = null,
  needAuth  = false,
  headers   = {},
} = {}) {
  const url  = `${API_ROOT}${path}`;
  const opts = { method, headers: { ...headers } };

  if (needAuth) {
    const token = localStorage.getItem("token");
    if (!token) throw new Error('No token found');
    opts.headers.Authorization = `Bearer ${token}`;
  }
  if (body != null) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }

  const res = await fetch(url, opts);

  if (!res.ok) {
    // swallow 404 → []
    if (ignore404 && res.status === 404) {
      return [];
    }
    // otherwise blow up
    const txt = await res.text();
    throw new Error(`Request failed: ${res.status} ${res.statusText} – ${txt}`);
  }

  return res.status === 204 ? null : res.json();
}

// ACCOUNTS

// Create an account
export const createAccount = ({ username, password, email, handle }) => 
    request('/accounts', {
        method: 'POST',
        body: { username, password, email, handle }
    });

// Login to an account
export const login = async ({ username, password }) => {
  const url  = `${BASE_BACKEND_URL}/api/accounts/login`;
  const body = new URLSearchParams({ username, password });
  const res  = await fetch(url, {
    method:  'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Login failed: ${res.status} ${res.statusText} – ${text}`);
  }
  return res.json(); // { access_token, token_type }
};

// This is to get the current user
export const getCurrentUser = () => 
    request('/accounts/me', { 
        needAuth: true 
    });

// This is to get all accounts
export const getAccounts = () =>
    request('/accounts');

// This is to get a specific account by username
export const getAccountByUsername = (username) => 
    request(`/accounts/${username}`);


// TWEETS

// This is to post a tweet
export const postTweet = ({ content, hashtags = [], media = [] }) => 
    request('/tweets', {
        method: 'POST',
        needAuth: true,
        body: { content, hashtags, media }
    });

// This is to delete a tweet
export const deleteTweet = (accountId, tweetId) => 
    request(`/${accountId}/tweets/${tweetId}`, {
        method: 'DELETE',
        needAuth: true
    });

// Edit a tweet
export const editTweet = (accountId, tweetId, { content, hashtags = [], media = [] }) => 
    request(`/${accountId}/tweets/${tweetId}`, {
        method: 'PUT',
        needAuth: true,
        body: { content, hashtags, media }
    });

// to get all tweets
export const getTweets = (q = null) => {
    const qs = q ? `?q=${encodeURIComponent(q)}` : '';
    request(`/tweets${qs}`)
}

// To like a tweet
export const likeTweet = (tweetId) => 
    request(`/tweets/${tweetId}/like`, {
        method: 'POST',
        needAuth: true
    });


// SEARCH

// Search for accounts
export const searchAccounts = (q) =>
  request('/accounts/search', {
    method:    'POST',
    body:      { query: q },
    ignore404: true,      // ← returns [] on 404
  });

export const searchHashtags = (q) =>
  request('/hashtags/search', {
    method:    'POST',
    body:      { query: q },
    ignore404: true,
  });

export const searchTweets = (q) =>
  request('/tweets/search', {
    method:    'POST',
    body:      { query: q },
    ignore404: true,
  });