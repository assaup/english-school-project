import { useState, useEffect } from 'react'
import api from '../../api/axios'
import type { UserShort } from '../../types'
import styles from './UsersAdminPage.module.scss'

const UsersAdminPage = () => {
    const [users, setUsers] = useState<UserShort[]>([])
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        let cancelled = false

        api.get<UserShort[]>('/users/').then(res => {
            if (!cancelled) {
                setUsers(res.data)
                setIsLoading(false)
            }
        })

        return () => { cancelled = true }
    }, [])

    const setRole = async (userId: number, role: 'teacher' | 'student') => {
        await api.post(`/users/${userId}/role/`, { role })
        setUsers(prev => prev.map(u =>
            u.id === userId ? { ...u, role } : u
        ))
    }

    return (
        <div className={styles.page}>
            <div className={styles.container}>
                <h1 className={styles.title}>Управление пользователями</h1>
                {isLoading ? <p>Загрузка...</p> : (
                    <table className={styles.table}>
                        <thead>
                            <tr>
                                <th>Пользователь</th>
                                <th>Текущая роль</th>
                                <th>Назначить роль</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(u => (
                                <tr key={u.id}>
                                    <td>{u.display}</td>
                                    <td>
                                        <span className={`${styles.badge} ${u.role ? styles[`badge_${u.role}`] : ''}`}>
                                            {u.role ?? '—'}
                                        </span>
                                    </td>
                                    <td className={styles.actions}>
                                        <button
                                            className={`${styles.btn} ${u.role === 'teacher' ? styles.btnActive : ''}`}
                                            onClick={() => setRole(u.id, 'teacher')}
                                            disabled={u.role === 'teacher'}
                                        >
                                            Учитель
                                        </button>
                                        <button
                                            className={`${styles.btn} ${u.role === 'student' ? styles.btnActive : ''}`}
                                            onClick={() => setRole(u.id, 'student')}
                                            disabled={u.role === 'student'}
                                        >
                                            Студент
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}

export default UsersAdminPage