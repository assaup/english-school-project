import { useState} from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'
import styles from './RegisterPage.module.scss'


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
        <div className={styles.page}>
            <div className={styles.card}>
                <div className={styles.header}>
                    <h1 className={styles.title}>Регистрация</h1>
                    <p className={styles.subtitle}>Создайте аккаунт и начните учиться</p>
                </div>

                {error && <p className={styles.error}>⚠ {error}</p>}

                <form onSubmit={handleSubmit} className={styles.form}>
                    <label className={styles.field}>
                        <span className={styles.label}>Имя пользователя</span>
                        <input
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            placeholder="Введите имя пользователя"
                            className={styles.input}
                            required
                            disabled={isLoading}
                        />
                    </label>

                    <label className={styles.field}>
                        <span className={styles.label}>Email</span>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="Введите ваш email"
                            className={styles.input}
                            required
                            disabled={isLoading}
                        />
                    </label>

                    <label className={styles.field}>
                        <span className={styles.label}>Пароль</span>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="Придумайте пароль"
                            className={styles.input}
                            required
                            disabled={isLoading}
                        />
                    </label>

                    <label className={styles.field}>
                        <span className={styles.label}>Подтверждение пароля</span>
                        <input
                            type="password"
                            name="passwordConfirm"
                            value={formData.passwordConfirm}
                            onChange={handleChange}
                            placeholder="Повторите пароль"
                            className={styles.input}
                            required
                            disabled={isLoading}
                        />
                    </label>

                    <button type="submit" className={styles.btn} disabled={isLoading}>
                        {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
                    </button>
                </form>

                <p className={styles.footer}>
                    Уже есть аккаунт?{' '}
                    <Link to="/login" className={styles.link}>Войти</Link>
                </p>
            </div>
        </div>
    )
}

export default RegisterPage