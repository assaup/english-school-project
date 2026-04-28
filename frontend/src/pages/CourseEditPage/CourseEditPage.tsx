import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../../api/axios'
import type { CourseDetail, Level, LessonWrite, UserShort, Enrollment } from '../../types'
import styles from '../CoursePage/CoursePage.module.scss'
import formStyles from './CourseEditPage.module.scss'

const CourseEditPage = () => {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const isCreate = !id

    const [formData, setFormData] = useState({
        title: '',
        description: '',
        level: '' as string | number,
        video_url: '',
    })
    const [levels, setLevels] = useState<Level[]>([])
    const [isLoading, setIsLoading] = useState(!isCreate)
    const [error, setError] = useState('')
    const [lessons, setLessons] = useState<LessonWrite[]>([])
    const [teachers, setTeachers] = useState<UserShort[]>([])
    const [enrollments, setEnrollments] = useState<Enrollment[]>([])
    const [newLesson, setNewLesson] = useState({ title: '', description: '', order: 0 })
    const [newTeacherId, setNewTeacherId] = useState('')
    const [newEnrollment, setNewEnrollment] = useState({ user: '', teacher: '', progress: 0, status: 'pending' })
    const [allTeachers, setAllTeachers] = useState<UserShort[]>([])
    const [allStudents, setAllStudents] = useState<UserShort[]>([])


    useEffect(() => {
        api.get<Level[]>('/levels/').then(res => setLevels(res.data)).catch(() => {})

        if (!isCreate) {
            api.get<LessonWrite[]>(`/courses/${id}/lessons/`).then(r => setLessons(r.data))
            api.get<UserShort[]>(`/courses/${id}/teachers/`).then(r => setTeachers(r.data))
            api.get<Enrollment[]>(`/courses/${id}/enrollments/`).then(r => setEnrollments(r.data))
            api.get<CourseDetail>(`/courses/${id}/`).then(res => {
                const c = res.data
                setFormData({
                    title: c.title,
                    description: c.description,
                    level: c.level?.id ?? '',
                    video_url: c.video_url,
                })
            }).catch(() => setError('Не удалось загрузить курс'))
            .finally(()=>setIsLoading(false))
        }
        api.get<UserShort[]>('/users/?role=teacher').then(r => setAllTeachers(r.data))
        api.get<UserShort[]>('/users/?role=student').then(r => setAllStudents(r.data))
    }, [id, isCreate])

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value}))
    }

    const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
        e.preventDefault()
        setError('')
        try {
            if (isCreate) {
                const res = await api.post<CourseDetail>('/courses/create/', formData)
                navigate(`/courses/${res.data.id}`)
            } else {
                await api.patch(`/courses/${id}/update/`, formData)
                navigate(`/courses/${id}`)
            }
        } catch {
            setError('Ошибка при сохранении')
        }
    }
    const addLesson = async () => {
        const res = await api.post<LessonWrite>(`/courses/${id}/lessons/`, newLesson)
        setLessons(prev => [...prev, res.data])
        setNewLesson({ title: '', description: '', order: 0 })
    }

    const deleteLesson = async (lessonId: number) => {
        await api.delete(`/lessons/${lessonId}/`)
        setLessons(prev => prev.filter(l => l.id !== lessonId))
    }

    const addTeacher = async () => {
        await api.post(`/courses/${id}/teachers/`, { user_id: newTeacherId })
        const res = await api.get<UserShort[]>(`/courses/${id}/teachers/`)
        setTeachers(res.data)
        setNewTeacherId('')
    }

    const removeTeacher = async (userId: number) => {
        await api.delete(`/courses/${id}/teachers/${userId}/`)
        setTeachers(prev => prev.filter(t => t.id !== userId))
    }

    const addEnrollment = async () => {
        const res = await api.post<Enrollment>(`/courses/${id}/enrollments/`, newEnrollment)
        setEnrollments(prev => [...prev, res.data])
        setNewEnrollment({ user: '', teacher: '', progress: 0, status: 'pending' })
    }

    const deleteEnrollment = async (enrollmentId: number) => {
        await api.delete(`/enrollments/${enrollmentId}/`)
        setEnrollments(prev => prev.filter(e => e.id !== enrollmentId))
    }
    if (isLoading) return <div className={styles.center}>Загрузка...</div>

    return (
        <div className={formStyles.page}>
            <div className={formStyles.card}>
                <div className={formStyles.header}>
                    <Link to={isCreate ? '/courses' : `/courses/${id}`} className={formStyles.back}>
                        ← Назад
                    </Link>
                    <h1 className={formStyles.title}>
                        {isCreate ? 'Создать курс' : 'Редактировать курс'}
                    </h1>
                </div>

                {error && <p className={formStyles.error}>⚠ {error}</p>}

                <form onSubmit={handleSubmit} className={formStyles.form}>
                    <label className={formStyles.field}>
                        <span className={formStyles.label}>Название *</span>
                        <input
                            type="text"
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            className={formStyles.input}
                            placeholder="Название курса"
                            required
                        />
                    </label>

                    <label className={formStyles.field}>
                        <span className={formStyles.label}>Описание</span>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            className={formStyles.textarea}
                            placeholder="Описание курса"
                            rows={4}
                        />
                    </label>

                    <label className={formStyles.field}>
                        <span className={formStyles.label}>Уровень</span>
                        <select
                            name="level"
                            value={formData.level}
                            onChange={handleChange}
                            className={formStyles.select}
                        >
                            <option value="">— Не выбран —</option>
                            {levels.map(l => (
                                <option key={l.id} value={l.id}>{l.name}</option>
                            ))}
                        </select>
                    </label>

                    <label className={formStyles.field}>
                        <span className={formStyles.label}>Ссылка на видео</span>
                        <input
                            type="url"
                            name="video_url"
                            value={formData.video_url}
                            onChange={handleChange}
                            className={formStyles.input}
                            placeholder="https://..."
                        />
                    </label>

                    <button type="submit" className={formStyles.btn}>
                        {isCreate ? 'Создать' : 'Сохранить'}
                    </button>
                </form>

                {!isCreate && (
                    <>
                        {/* Уроки */}
                        <div className={formStyles.inlineSection}>
                            <h2 className={formStyles.inlineTitle}>Уроки</h2>
                            <table className={formStyles.table}>
                                <thead>
                                    <tr>
                                        <th>Порядок</th><th>Название</th><th>Описание</th><th></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {lessons.map(l => (
                                        <tr key={l.id}>
                                            <td>{l.order}</td>
                                            <td>{l.title}</td>
                                            <td>{l.description?.slice(0, 50)}{l.description?.length > 50 ? '...' : ''}</td>
                                            <td>
                                                <button
                                                    type="button"
                                                    className={formStyles.btnDanger}
                                                    onClick={() => deleteLesson(l.id)}
                                                >
                                                    Удалить
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            <div className={formStyles.inlineAdd}>
                                <input
                                    type="number"
                                    placeholder="Порядок"
                                    value={newLesson.order}
                                    onChange={e => setNewLesson(p => ({ ...p, order: +e.target.value }))}
                                    className={formStyles.inputSmall}
                                />
                                <input
                                    type="text"
                                    placeholder="Название урока"
                                    value={newLesson.title}
                                    onChange={e => setNewLesson(p => ({ ...p, title: e.target.value }))}
                                    className={formStyles.input}
                                />
                                <input
                                    type="text"
                                    placeholder="Описание"
                                    value={newLesson.description}
                                    onChange={e => setNewLesson(p => ({ ...p, description: e.target.value }))}
                                    className={formStyles.input}
                                />
                                <button type="button" onClick={addLesson} className={formStyles.btnAdd}>
                                    + Добавить урок
                                </button>
                            </div>
                        </div>

                        {/* Преподаватели */}
                        <div className={formStyles.inlineSection}>
                            <h2 className={formStyles.inlineTitle}>Преподаватели курса</h2>
                            <table className={formStyles.table}>
                                <thead><tr><th>Преподаватель</th><th></th></tr></thead>
                                <tbody>
                                    {teachers.map(t => (
                                        <tr key={t.id}>
                                            <td>{t.display}</td>
                                            <td>
                                                <button
                                                    type="button"
                                                    className={formStyles.btnDanger}
                                                    onClick={() => removeTeacher(t.id)}
                                                >
                                                    Удалить
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            <div className={formStyles.inlineAdd}>
                                <select
                                    value={newTeacherId}
                                    onChange={e => setNewTeacherId(e.target.value)}
                                    className={formStyles.select}
                                >
                                    <option value="">— Выбрать преподавателя —</option>
                                    {allTeachers.map(u => (
                                        <option key={u.id} value={u.id}>{u.display}</option>
                                    ))}
                                </select>
                                <button type="button" onClick={addTeacher} className={formStyles.btnAdd}>
                                    + Добавить
                                </button>
                            </div>
                        </div>

                        {/* Записи */}
                        <div className={formStyles.inlineSection}>
                            <h2 className={formStyles.inlineTitle}>Записи на курс</h2>
                            <table className={formStyles.table}>
                                <thead>
                                    <tr><th>Студент</th><th>Преподаватель</th><th>Прогресс</th><th>Статус</th><th></th></tr>
                                </thead>
                                <tbody>
                                    {enrollments.map(e => (
                                        <tr key={e.id}>
                                            <td>{e.user_display}</td>
                                            <td>{e.teacher_display ?? '—'}</td>
                                            <td>{e.progress}%</td>
                                            <td>{e.status}</td>
                                            <td>
                                                <button
                                                    type="button"
                                                    className={formStyles.btnDanger}
                                                    onClick={() => deleteEnrollment(e.id)}
                                                >
                                                    Удалить
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            <div className={formStyles.inlineAdd}>
                                <select
                                    value={newEnrollment.user}
                                    onChange={e => setNewEnrollment(p => ({ ...p, user: e.target.value }))}
                                    className={formStyles.select}
                                >
                                    <option value="">— Студент —</option>
                                    {allStudents.map(u => (
                                        <option key={u.id} value={u.id}>{u.display}</option>
                                    ))}
                                </select>
                                <select
                                    value={newEnrollment.teacher}
                                    onChange={e => setNewEnrollment(p => ({ ...p, teacher: e.target.value }))}
                                    className={formStyles.select}
                                >
                                    <option value="">— Преподаватель —</option>
                                    {allTeachers.map(u => (
                                        <option key={u.id} value={u.id}>{u.display}</option>
                                    ))}
                                </select>
                                <button type="button" onClick={addEnrollment} className={formStyles.btnAdd}>
                                    + Записать
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    )
}
export default CourseEditPage