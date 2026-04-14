import { useEffect, useState } from "react"
import { useParams, Link, useNavigate } from "react-router-dom"
import api from "../../api/axios"
import type { Course, Lesson } from "../../types"
import styles from "./CourseDetailPage.module.scss"

export function CourseDetailPage() {
    const { id } = useParams<{ id: string }>()
    const [course, setCourse] = useState<Course | null>(null)
    const [lessons, setLessons] = useState<Lesson[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")
    const navigate = useNavigate()

    useEffect(() => {
        const fetchCourse = async () => {
            try {
                const [courseRes, lessonsRes] = await Promise.all([
                    api.get<Course>(`/courses/${id}/`),
                    api.get<Lesson[]>(`/courses/${id}/lessons/`)
                ])
                setCourse(courseRes.data)
                setLessons(lessonsRes.data)
            } catch {
                setError("Не удалось загрузить курс")
            } finally {
                setLoading(false)
            }
        }

        fetchCourse()
    }, [id])

    if (loading) {
        return <div className={styles.loading}>Загрузка...</div>
    }

    if (error || !course) {
        return <div className={styles.error}>{error || "Курс не найден"}</div>
    }

    return (
        <div className={styles.courseDetailPage}>
            <div className={styles.header}>
                <Link to="/courses" className={styles.backLink}>
                    ← Назад к курсам
                </Link>
            </div>

            <div className={styles.content}>
                <h1 className={styles.title}>{course.title}</h1>
                <p className={styles.instructor}>
                    Преподаватель: {course.instructor}
                </p>
                <p className={styles.description}>{course.description}</p>

                <div className={styles.lessonsSection}>
                    <h2 className={styles.lessonsTitle}>Уроки</h2>
                    
                    {lessons.length === 0 ? (
                        <p className={styles.noLessons}>Уроков пока нет</p>
                    ) : (
                        <ul className={styles.lessonsList}>
                            {lessons.map((lesson, index) => (
                                <li key={lesson.id} className={styles.lessonItem}>
                                    <span className={styles.lessonNumber}>
                                        {index + 1}
                                    </span>
                                    <div className={styles.lessonInfo}>
                                        <h3 className={styles.lessonTitle}>
                                            {lesson.title}
                                        </h3>
                                    </div>
                                    <button
                                        onClick={() => navigate(`/courses/${id}/lessons/${lesson.id}`)}
                                        className={styles.viewButton}
                                    >
                                        Открыть
                                    </button>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    )
}
