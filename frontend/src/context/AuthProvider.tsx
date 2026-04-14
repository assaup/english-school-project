import { useState, useEffect } from "react"
import type { ReactNode } from "react"
import api from "../api/axios"
import { AuthContext } from "./AuthContext"
import type { User, AuthTokens } from "../types"

interface Props {
    children: ReactNode
}

export function AuthProvider({ children }: Props) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const initAuth = async () => {
            try {
                const token = localStorage.getItem('access')

                if (!token) {
                    setUser(null)
                    return
                }

                const res = await api.get<User>('/me/')
                setUser(res.data)
            } catch {
                setUser(null)
                localStorage.removeItem('access')
            } finally {
                setLoading(false)
            }
        }

        initAuth()
    }, [])

    const login = async (username: string, password: string) => {
        const { data } = await api.post<AuthTokens>('/auth/login/', { username, password })
        localStorage.setItem('access', data.access)
        localStorage.setItem('refresh', data.refresh)

        const me = await api.get<User>('/me/')
        setUser(me.data)
    }

    const logout = () => {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    )
}
