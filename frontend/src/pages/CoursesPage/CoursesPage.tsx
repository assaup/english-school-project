import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import api from "../../api/axios"
import type { Course } from "../../types"
import styles from "./CoursesPage.module.scss"

export function CoursesPage() {
    const [courses, setCourses] = useState<Course[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    useEffect(() => {
        const fetchCourses = async () => {
            try {
                const response = await api.get<Course[]>("/courses/")
                setCourses(response.data)
            } catch {
                setError("Не удалось загрузить курсы")
            } finally {
                setLoading(false)
            }
        }

        fetchCourses()
    }, [])

    if (loading) {
        return <div className={styles.loading}>Загрузка...</div>
    }

    if (error) {
        return <div className={styles.error}>{error}</div>
    }

    return (
        <div className={styles.coursesPage}>
            <div className={styles.header}>
                <h1 className={styles.title}>Курсы</h1>
                <Link to="/courses/new" className={styles.newCourseButton}>
                    + Новый курс
                </Link>
            </div>

            {courses.length === 0 ? (
                <div className={styles.empty}>
                    <p>Курсов пока нет</p>
                </div>
            ) : (
                <div className={styles.grid}>
                    {courses.map((course) => (
                        <Link
                            key={course.id}
                            to={`/courses/${course.id}`}
                            className={styles.card}
                        >
                            <h2 className={styles.cardTitle}>{course.title}</h2>
                            <p className={styles.description}>{course.description}</p>
                            <div className={styles.footer}>
                                <span className={styles.instructor}>
                                    Преподаватель: {course.instructor}
                                </span>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    )
}
