import { useState, useEffect } from 'react';
import styles from './SideMenu.module.css';
import { Link, useNavigate } from 'react-router-dom';
import { getCurrentUser } from '../../services/api'; 

export default function SideMenu() {
    const [user, setUser] = useState(null);
    const Navigate = useNavigate();

    useEffect(() => {
    // load current user (if logged in)
    getCurrentUser()
      .then(setUser)
      .catch(() => { /* no-op if not authenticated */ });
    }, []);

    // function to handle logout
    const handleLogout = () => {
        localStorage.removeItem('token');
        setUser(null);
        Navigate('/login');
    };

    return (
        <div className={styles.menu__side}>
            <div>
                <div>
                    <h1 className={styles.menu__side__logo}>Z</h1>
                    <ul className={styles.menu__side__list}>
                        <li className={styles.menu__side__list__item}> 
                            <Link className={styles.menu__side__list__item__link} to="/">Home</Link>
                        </li>
                        <li className={styles.menu__side__list__item}> 
                            <Link 
                                className={styles.menu__side__list__item__link} 
                                to={`/${user?.username}/profile`}>
                                Profile
                            </Link>
                        </li>
                        <li className={styles.menu__side__list__item}>More</li>
                    </ul>
                </div>

                <div>
                    <button className={styles.menu__side__button}>
                        Post
                    </button>
                </div>
            </div>

            <div className={styles.menu__side__user}>
                <div>
                    <img 
                        src="../../../public/pepefrog.jpg" 
                        alt="profilepic"
                        className={styles.menu__side__user__img} 
                    />
                </div>
                <div>
                    <Link 
                        to={`/${user?.username}/profile`} 
                        className={styles.menu__side__user__name}
                    >
                        {user ? user.username : 'Loading...'}
                    </Link>
                    <p className={styles.menu__side__user__handle}>
                        @{user ? user.handle : ''}
                    </p>
                </div>
                <div className={styles.menu__side__user__button}>
                    <button onClick={handleLogout}>bye bye button</button>
                </div>
            </div>
        </div>
    );
}