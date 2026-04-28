import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../../api/axios'
import type { Course } from '../../types'
import CourseCard from '../../components/CourseCard/CourseCard'
import styles from './CoursesPage.module.scss'

const CoursesPage = () => {
    const [courses, setCourses] = useState<Course[]>([])
    const [search, setSearch] = useState('')
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState('')

    const fetchCourses = async (q = '') => {
        setIsLoading(true)
        setError('')
        try {
            const res = await api.get<Course[]>('/courses/', {
                params: q ? { search: q } : {}
            })
            setCourses(res.data)
        } catch {
            setError('Не удалось загрузить курсы')
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        const timer = setTimeout(() => fetchCourses(search), 400)
        return () => clearTimeout(timer)
    }, [search])

    return (
        <div className={styles.page}>
            <div className={styles.hero}>
                <div className={styles.heroContent}>
                    <h1 className={styles.heroTitle}>Все курсы</h1>
                    <p className={styles.heroText}>Выберите курс и начните учиться уже сегодня</p>
                </div>
            </div>

            <div className={styles.container}>
                <div className={styles.toolbar}>
                    <input
                        type="text"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        placeholder="Найти курс..."
                        className={styles.searchInput}
                    />
                    <Link to="/courses/create" className={styles.btnCreate}>
                        + Создать курс
                    </Link>
                </div>

                {isLoading && <p className={styles.empty}>Загрузка...</p>}
                {error && <p className={styles.error}>{error}</p>}

                {!isLoading && !error && (
                    <>
                        {courses.length === 0 ? (
                            <p className={styles.empty}>Курсы не найдены</p>
                        ) : (
                            <div className={styles.grid}>
                                {courses.map(course => (
                                    <CourseCard key={course.id} course={course} />
                                ))}
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    )
}

export default CoursesPage