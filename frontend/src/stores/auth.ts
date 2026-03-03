import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/app'

export const useAuthStore = defineStore('auth', () => {
    // 默认已登录（无需真实认证，直接进入系统）
    const user = ref<User>({
        id: 'student_001',
        name: '学习者',
        email: 'student@aischool.com',
        role: 'student',
        avatar: ''
    })

    const token = ref<string>(localStorage.getItem('token') || 'mock-token')

    const isAuthenticated = computed(() => !!token.value)

    const login = async (email: string, _password: string) => {
        // 简单 mock 登录
        user.value = {
            id: 'student_001',
            name: email.split('@')[0],
            email,
            role: 'student'
        }
        token.value = 'mock-token'
        localStorage.setItem('token', token.value)
    }

    const logout = () => {
        token.value = ''
        localStorage.removeItem('token')
    }

    return { user, token, isAuthenticated, login, logout }
})
