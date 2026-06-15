import { Link } from 'react-router-dom'
import styles from './ForbiddenPage.module.scss'

const ForbiddenPage = () => {
    return (
        <div className={styles.page}>
            <div className={styles.card}>
                <div className={styles.code}>403</div>
                <h1 className={styles.title}>Доступ запрещён</h1>
                <p className={styles.subtitle}>
                    У вас недостаточно прав для просмотра этой страницы.
                </p>
                <Link to="/" className={styles.btn}>
                    На главную
                </Link>
            </div>
        </div>
    )
}

export default ForbiddenPage
