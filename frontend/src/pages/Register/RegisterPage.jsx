import styles from './RegisterPage.module.css';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createAccount } from '../../services/api';

export default function RegisterPage() {
    const [error, setError] = useState(null)
    const [formData, setFormData] = useState({
        username: '',
        handle: '',
        email: '',
        password: '',
        confirmPassword: ''
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (formData.password !== formData.confirmPassword) {
        setError("Passwords don't match");
        return;
        }

        // strip out confirmPassword before sending
        const { confirmPassword, ...cleanData } = formData;

        try {
        // call api.js helper instead of fetch
        await createAccount(cleanData);
        navigate('/login');
        } catch (err) {
        // createAccount() will throw with status/text baked in
        setError(err.message);
        }
    };

    return (
        <div className={styles.register}>
            <h1>Create an Account</h1>
            <form className={styles.register__form} onSubmit={handleSubmit}>
                <div className={styles.register__form__name}>
                    <label htmlFor="username">Username</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className={styles.register__form__name}>
                    <label htmlFor="handle">Handle</label>
                    <input
                        type="text"
                        id="handle"
                        name="handle"
                        value={formData.handle}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className={styles.register__form__email}>
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className={styles.register__form__password}>
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className={styles.register__form__confirm}>
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className={styles.register__form__button}>
                    <button type="submit">Register</button>
                    {error && <p>{error}</p>}
                </div>
            </form>
        </div>
    );
}