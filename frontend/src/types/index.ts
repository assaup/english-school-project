export interface Level {
    id: number
    name: string
    description: string
}

export interface User {
    id: number
    username: string
    first_name: string
    last_name: string
    email: string
    level: Level | null
}

export interface ExerciseType {
    id: number
    name: string
}

export interface Exercise {
    id: number
    question: string
    correct_answer: string
    exercise_type: ExerciseType | null
    order: number
}

export interface Lesson {
    id: number
    title: string
    description: string
    order: number
    exercises: Exercise[]
}

export interface Course {
    id: number
    title: string
    description: string
    level: Level | null
    lessons_count?: number
    teachers_count?: number
    lessons?: Lesson[]
    teachers?: User[]
    cover: string | null
    video_url: string
    created_at: string
}

export interface UserCourse{
    id: number
    course: Course
    progress: number
    status: 'pending' | 'active' | 'finished'
    enrolled_at: string
    access_until: string | null
}

export interface Result {
    id: number
    exercise: Exercise
    user_answer: string
    score: number
    completed_at: string
}

export interface Stats {
    total_courses: number
    total_students: number
    avg_score: number | null
    course_stats: {
        title: string
        level__name: string
        students_count: number
    }[]
}

export interface AuthTokens {
    access: string
    refresh: string
}

export interface PaginatedResponse<T>{
    count: number
    next: string | null
    previous: string | null
    results: T[]
}