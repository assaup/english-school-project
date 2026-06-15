import { Navigate } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useAuth } from '../../context/useAuth'

interface Props {
    children: ReactNode
    allowedRoles: ('admin' | 'teacher' | 'student')[]
}

const ProtectedRoute = ({ children, allowedRoles }: Props) => {
    const { user, loading } = useAuth()

    if (loading) return null

    if (!user) return <Navigate to="/login" replace />

    if (!user.role || !allowedRoles.includes(user.role)) {
        return <Navigate to="/403" replace />
    }

    return <>{children}</>
}

export default ProtectedRoute
