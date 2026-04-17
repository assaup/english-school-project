import { Link } from 'react-router-dom'
import styles from './Footer.module.scss'

const Footer = () => {
    return (
        <footer className={styles.footer}>
            <div className={styles.container}>
                <div className={styles.top}>
                    <div className={styles.brand}>
                        <span className={styles.logo}>🎓 ENGLOBE</span>
                        <p>Онлайн-школа с системным подходом и сильными преподавателями</p>
                    </div>

                    <div className={styles.nav}>
                        <div className={styles.navCol}>
                            <h4>Обучение</h4>
                            <Link to="/">Курсы</Link>
                            <Link to="/">Преподаватели</Link>
                            <Link to="/">Первый урок бесплатно</Link>
                        </div>
                        <div className={styles.navCol}>
                            <h4>Аккаунт</h4>
                            <Link to="/login">Войти</Link>
                            <Link to="/register">Регистрация</Link>
                            <Link to="/dashboard">Личный кабинет</Link>
                        </div>
                    </div>
                </div>

                <div className={styles.bottom}>
                    <p>© {new Date().getFullYear()} ENGLOBE. Все права защищены.</p>
                    <div className={styles.bottomLinks}>
                        <a href="#">Политика конфиденциальности</a>
                        <a href="#">Пользовательское соглашение</a>
                    </div>
                </div>
            </div>
        </footer>
    )
}

export default Footer