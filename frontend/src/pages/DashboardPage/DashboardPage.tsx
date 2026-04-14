import { useAuth } from "../../context/useAuth"
import styles from "./DashboardPage.module.scss"

export function DashboardPage() {
    const { user, logout } = useAuth()

    return (
        <div className={styles.dashboardPage}>
            <div className={styles.header}>
                <h1 className={styles.title}>Панель управления</h1>
                <button onClick={logout} className={styles.logoutButton}>
                    Выйти
                </button>
            </div>

            <div className={styles.content}>
                <div className={styles.welcomeCard}>
                    <h2 className={styles.welcomeTitle}>
                        Добро пожаловать, {user?.username || "Пользователь"}!
                    </h2>
                    {user?.email && (
                        <p className={styles.email}>{user.email}</p>
                    )}
                </div>

                <div className={styles.cardsGrid}>
                    <a href="/courses" className={styles.card}>
                        <h3 className={styles.cardTitle}>Курсы</h3>
                        <p className={styles.cardDescription}>
                            Просмотр и управление курсами
                        </p>
                    </a>
                    
                    <a href="/profile" className={styles.card}>
                        <h3 className={styles.cardTitle}>Профиль</h3>
                        <p className={styles.cardDescription}>
                            Настройки аккаунта
                        </p>
                    </a>
                </div>
            </div>
        </div>
    )
}
