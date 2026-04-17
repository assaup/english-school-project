import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'
import Button from '../Button/Button'
import styles from './Navbar.module.scss'

const Navbar = () => {
    const { user, logout } = useAuth()
    const navigate = useNavigate()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <header className={styles.header}>
            <div className={styles.container}>
                <Link to="/" className={styles.logo}>
                    🎓 ENGLOBE
                </Link>
                <nav className={styles.nav}>
                    <select name="clients" className={`${styles.navLink} ${styles.navLink__select}`}>
                        <option value="">Для взрослых</option>
                        <option value="">Для детей и подростков</option>
                        <option value="">Премиальный тариф</option>
                        <option value="">Для компаний</option>
                        <option value="">Видеокурсы</option>
                    </select>
                    <Link to="/" className={styles.navLink}>Преподаватели</Link>
                    <Link to="/" className={styles.navLink}>Курсы</Link>
                    <Link to="/" className={styles.navLink}>Стоимость</Link>
                </nav>
                <div className={styles.buttons}>
                    {user ? (
                        <>
                            <Link to="/dashboard" className={styles.navLink}>
                                {user.first_name || user.username}
                            </Link>
                            <Button type='button' onClick={handleLogout} className={styles.button}>
                                Выйти
                            </Button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className={styles.navLink}>Войти</Link>
                            <Link to="/register" className={styles.navLink}>
                                Регистрация
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </header>
    )
}

export default Navbar