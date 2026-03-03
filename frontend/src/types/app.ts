export interface AppError {
    title: string
    message: string
    details?: any
    timestamp: number
}

export interface Notification {
    id: string
    title: string
    message: string
    type: 'success' | 'warning' | 'info' | 'error'
    duration?: number
    action?: {
        label: string
        handler: () => void
    }
}

export interface User {
    id: string
    name: string
    email: string
    role: 'student' | 'teacher' | 'admin'
    avatar?: string
}
