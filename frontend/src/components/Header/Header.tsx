import { NavLink } from "react-router-dom"
import { useAuth } from "../../context/useAuth"
import styles from "./Header.module.scss"

export function Header() {
    const { user, logout } = useAuth()

    return (
        <header className={styles.header}>
            <NavLink to="/dashboard" className={styles.logo}>
                LMS
            </NavLink>

            {user && (
                <nav className={styles.nav}>
                    <NavLink
                        to="/courses"
                        className={({ isActive }) =>
                            `${styles.navLink} ${isActive ? styles.active : ""}`
                        }
                    >
                        Курсы
                    </NavLink>

                    <div className={styles.userMenu}>
                        <span className={styles.userName}>
                            {user.username}
                        </span>
                        <button onClick={logout} className={styles.logoutButton}>
                            Выйти
                        </button>
                    </div>
                </nav>
            )}
        </header>
    )
}
