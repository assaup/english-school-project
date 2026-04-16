import { useState} from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'


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
        <div className="loginPage">
            <h1>Вход в систему</h1>
            <form onSubmit={handleSubmit}>
                {isLoading && (
                    <p>Загрузка...</p>

                )}
                {error && (
                    <p>Ошибка: {error}</p>
                )}

                <label>
                    Имя пользователя
                    <input 
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className=''
                        placeholder='Введите имя пользователя'
                        required
                        disabled={isLoading}
                    />
                </label>
                <label>
                    Пароль
                    <input 
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className=''
                        placeholder='Введите пароль'
                        required
                        disabled={isLoading}
                    />
                </label>

                <button type='submit' className='' disabled={isLoading}>
                    {isLoading ? 'Вход...' : 'Войти'}
                </button>

                <p>
                    Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
                </p>
            </form>
        </div>
    )
}

export default LoginPage