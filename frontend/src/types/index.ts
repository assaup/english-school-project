export interface User {
    id: number
    username: string
    email: string
    first_name?: string
    last_name?: string
}

export interface AuthTokens {
    access: string
    refresh: string
}

export interface Course {
    id: number
    title: string
    description: string
    instructor: string
    created_at: string
    updated_at: string
}

export interface Lesson {
    id: number
    title: string
    content: string
    course: number
    order: number
    created_at: string
}
