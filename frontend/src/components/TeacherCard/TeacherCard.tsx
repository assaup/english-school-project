import type { Teacher } from '../../types'
import styles from './TeacherCard.module.scss'

interface Props {
    teacher: Teacher
}

const TeacherCard = ({ teacher }: Props) => {
    return (
        <div key={teacher.id} className={styles.teacherCard}>
            <div className={styles.teacherAvatar}>
            </div>
            <div className={styles.teacherInfo}>
                <h3>
                    {teacher.first_name && teacher.last_name
                        ? `${teacher.first_name} ${teacher.last_name}`
                        : teacher.username}
                </h3>
                {teacher.level && (
                    <span className={styles.levelBadge}>Уровень: {teacher.level.name}</span>
                )}
                {teacher.courses_count ? <p>Количество курсов: {teacher.courses_count}</p> : ''}
                
            </div>
        </div>
    )
}

export default TeacherCard