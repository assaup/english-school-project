import { useState, type FormEvent } from "react"
import { useNavigate, Link } from "react-router-dom"
import { useAuth } from "../../context/useAuth"
import styles from "./LoginPage.module.scss"

export function LoginPage() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const [isLoading, setIsLoading] = useState(false)

    const { login } = useAuth()
    const navigate = useNavigate()

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()
        setError("")
        setIsLoading(true)

        try {
            await login(username, password)
            navigate("/dashboard")
        } catch (err) {
            setError("Неверное имя пользователя или пароль")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className={styles.loginPage}>
            <div className={styles.loginContainer}>
                <h1 className={styles.title}>Вход в систему</h1>
                
                <form onSubmit={handleSubmit} className={styles.form}>
                    {error && (
                        <div className={styles.error}>{error}</div>
                    )}

                    <div className={styles.formGroup}>
                        <label htmlFor="username" className={styles.label}>
                            Имя пользователя
                        </label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className={styles.input}
                            placeholder="Введите имя пользователя"
                            required
                            disabled={isLoading}
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="password" className={styles.label}>
                            Пароль
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className={styles.input}
                            placeholder="Введите пароль"
                            required
                            disabled={isLoading}
                        />
                    </div>

                    <button
                        type="submit"
                        className={styles.submitButton}
                        disabled={isLoading}
                    >
                        {isLoading ? "Вход..." : "Войти"}
                    </button>
                </form>

                <p className={styles.footer}>
                    Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
                </p>
            </div>
        </div>
    )
}
