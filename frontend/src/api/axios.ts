import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import type { AuthTokens } from "../types";

const api = axios.create({
    baseURL: '/api',
    headers: {
        "Content-Type": 'application/json'
    }
})

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access')
    if (token){
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

api.interceptors.response.use(
    response => response,
    async (error: AxiosError) => {
        const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
        
        if (error.response?.status === 401 && !original._retry){
            original._retry = true

            try{
                const refresh = localStorage.getItem('refresh')
                if (!refresh) throw new Error('No refresh token')

                const { data } = await axios.post<AuthTokens>('/api/auth/refresh/', { refresh })
                localStorage.setItem('access', data.access)
                original.headers.Authorization = `Bearer ${data.access}`

                return api(original)
            } catch {
                localStorage.removeItem('access')
                localStorage.removeItem('refresh')
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)


export default api
