import { useState, useEffect } from 'react'
import { useParams, useNavigate} from 'react-router-dom'
import api from '../../api/axios'
import type { CourseDetail } from '../../types'
import Button from '../../components/Button/Button'
import TeacherSlider from '../../components/TeacherSlider/TeacherSlider'
import type { Teacher } from '../../types'
import styles from './CoursePage.module.scss'
import FormCard from '../../components/FormCard/FormCard'


const CoursePage = () => {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [course, setCourse] = useState<CourseDetail | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState('')
    const [showDeleteModal, setShowDeleteModal] = useState(false)

    useEffect(() => {
        const fetch = async () => {
            try {
                const res = await api.get<CourseDetail>(`/courses/${id}/`)
                setCourse(res.data)
            } catch {
                setError('Курс не найден')
            } finally {
                setIsLoading(false)
            }
        }
        fetch()
    }, [id])

    const handleDelete = async () => {
        try {
            await api.delete(`/courses/${id}/delete/`)
            navigate('/courses')
        } catch {
            setError('Ошибка при удалении')
        }
    }

    if (isLoading) return <p className={styles.center}>Загрузка...</p>
    if (error || !course) return  <p className={styles.center}>{error}</p>

    return (
        <div className={styles.container}>
            {/* Hero курса */}
            <section className={styles.hero}>
                <div className={styles.heroContent}>
                    <div className={styles.heroMeta}>
                        <div className={styles.info}>
                            <img src="https://englex.ru/app/uploads/2026/02/icon_sale_24x24.svg" alt="" />
                            <p>Скидка до 50%</p>
                        </div>
                        <div className={styles.info}>
                            {course.level && <span className={styles.badge}>{course.level.name}</span>}
                            {new Date(course.created_at).toLocaleDateString('ru-RU')}
                        </div>
                    </div>
                    <h1 className={styles.titleFirst}>{course.title}</h1>
                    <p className={styles.description}>{course.description}</p>

                    <div className={styles.stats}>
                        <div className={styles.stat}>
                            <strong>{course.lessons?.length ?? 0}</strong>
                            <span>уроков</span>
                        </div>

                        <div className={styles.stat}>
                            <strong>{course.teachers?.length ?? 0}</strong>
                            <span>преподавателей</span>
                        </div>
                    </div>

                    <div className={styles.actions}>
                        <Button 
                            type='button' 
                            variant="light"
                            onClick={() => navigate(`/courses/${id}/edit`)}
                        >
                            Редактировать
                        </Button>
                        <Button
                            type='button'
                            onClick={() => setShowDeleteModal(true)}
                        >
                            Удалить
                        </Button>
                    </div>
                </div>

                <div>
                    <FormCard />
                </div>
            </section>

            {course.teachers.length > 0 && (
                    <section className={styles.section}>
                        <h2 className={styles.section__title}>Преподаватели курса</h2>
                            <p className={styles.section__text}>
                                Опытные специалисты, которые проведут вас через всю программу курса
                            </p>
                            <TeacherSlider teachers={course.teachers ?? [] as Teacher[]}/>
                    </section>
                )}
            {/* Уроки */}
            <section className={styles.section}>
                <h2 className={styles.section__title}>Программа курса</h2>
                {course.lessons && course.lessons.length > 0 ? (
                    <div className={styles.lessons}>
                        {course.lessons.map((lesson, idx) => (
                            <div key={lesson.id} className={styles.lessonCard}>
                                <div className={styles.lessonNum}>{idx + 1}</div>
                                <div className={styles.lessonInfo}>
                                    <h3 className={styles.lessonTitle}>{lesson.title}</h3>
                                    {lesson.description && (
                                        <p className={styles.lessonDesc}>{lesson.description}</p>
                                    )}
                                    {lesson.exercises.length > 0 && (
                                        <span className={styles.exerciseBadge}>
                                            {lesson.exercises.length} заданий
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className={styles.empty}>Уроки ещё не добавлены</p>
                )}
            </section>

            {/* Модалка удаления */}
            {showDeleteModal && (
                <div className={styles.modal}>
                    <div className={styles.modalBox}>
                        <h3 className={styles.modalBox__title}>Удалить курс?</h3>
                        <p>«{course.title}» будет удалён безвозвратно.</p>
                        <div className={styles.modalActions}>
                            <Button onClick={() => setShowDeleteModal(false)} variant='light'>
                                Отмена
                            </Button>
                            <Button onClick={handleDelete}>
                                Удалить
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )

}

export default CoursePage