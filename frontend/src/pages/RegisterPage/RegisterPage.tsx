import { useState} from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'


const RegisterPage = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        passwordConfirm: '',
    })
    const [error, setError] = useState('')
    const [isLoading, setIsLoading] = useState(false)


    const { register } = useAuth()
    const navigate = useNavigate()

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const {name, value} = e.target
        setFormData( prev => ({
            ...prev,
            [name]: value
        }))
    }
    const handleSubmit = async (e: React.SubmitEvent) => {
        e.preventDefault()
        setError('')
        
        if (formData.password !== formData.passwordConfirm){
            setError('Пароли не совпадают')
            return
        }

        if (formData.password.length < 6) {
            setError('Пароль должен содержать минимум 6 символов');
            return;
        }

        setIsLoading(true)

        try {
            await register(
                formData.username,
                formData.email,
                formData.password,
                formData.passwordConfirm
            )
            navigate('/dashboard')
        } catch(err: any) {
            setError(err.response?.data?.detail ||
                err.response?.data?.username?.[0] ||
                err.response?.data?.email?.[0] ||
                err.message ||
                'Ошибка при регистрации')
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="loginPage">
            <h1>Регистрация</h1>
            <form onSubmit={handleSubmit}>
                {isLoading && <p>Загрузка...</p>}
                {error && <p>Ошибка: {error}</p>}

                <label>
                    Имя пользователя
                    <input 
                        type="text"
                        name='username'
                        value={formData.username}
                        onChange={handleChange}
                        className=''
                        placeholder='Введите имя пользователя'
                        required
                        disabled={isLoading}
                    />
                </label>

                <label>
                    Email
                    <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="Введите ваш email"
                        required
                        disabled={isLoading}
                    />
                </label>

                <label>
                    Пароль
                    <input 
                        type="password"
                        name='password'
                        value={formData.password}
                        onChange={handleChange}
                        className=''
                        placeholder='Придумайте пароль'
                        required
                        disabled={isLoading}
                    />
                </label>

                <label>
                    Подтверждение пароля
                    <input
                        type="password"
                        name="passwordConfirm"
                        value={formData.passwordConfirm}
                        onChange={handleChange}
                        placeholder="Повторите пароль"
                        required
                        disabled={isLoading}
                    />
                </label>

                <button type='submit' className='' disabled={isLoading}>
                    {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
                </button>

                <p>
                    Уже есть аккаунт? <Link to="/login">Войти</Link>
                </p>
            </form>
        </div>
    )
}

export default RegisterPage