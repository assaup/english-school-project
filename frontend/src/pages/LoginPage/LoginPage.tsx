import { useState} from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'
import styles from './LoginPage.module.scss'


const LoginPage = () => {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [isLoading, setIsLoading] = useState(false)


    const { login } = useAuth()
    const navigate = useNavigate()

    const handleSubmit = async (e: React.SubmitEvent) => {
        e.preventDefault()
        setError('')
        setIsLoading(true)

        try {
            await login(username, password)
            navigate('/dashboard')
        } catch {
            setError("Неверное имя пользователя или пароль")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className={styles.page}>
            <div className={styles.card}>
                <div className={styles.header}>
                    <h1 className={styles.title}>Вход в систему</h1>
                    <p className={styles.subtitle}>Рады видеть вас снова</p>
                </div>

                {error && <p className={styles.error}>⚠ {error}</p>}

                <form onSubmit={handleSubmit} className={styles.form}>
                    <label className={styles.field}>
                        <span className={styles.label}>Имя пользователя</span>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Введите имя пользователя"
                            className={styles.input}
                            required
                            disabled={isLoading}
                        />
                    </label>

                    <label className={styles.field}>
                        <span className={styles.label}>Пароль</span>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Введите пароль"
                            className={styles.input}
                            required
                            disabled={isLoading}
                        />
                    </label>

                    <button type="submit" className={styles.btn} disabled={isLoading}>
                        {isLoading ? 'Вход...' : 'Войти'}
                    </button>
                </form>

                <p className={styles.footer}>
                    Нет аккаунта?{' '}
                    <Link to="/register" className={styles.link}>
                        Зарегистрироваться
                    </Link>
                </p>
            </div>
        </div>
    )
}

export default LoginPage