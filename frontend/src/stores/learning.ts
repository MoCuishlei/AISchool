import { defineStore } from 'pinia'
import { ref } from 'vue'
import { quickTeach, generatePractice, checkHealth } from '@/api/learning'

export const useLearningStore = defineStore('learning', () => {
    const isLoading = ref(false)
    const backendStatus = ref<'unknown' | 'healthy' | 'unhealthy'>('unknown')
    const currentContent = ref<string>('')
    const currentPractice = ref<string>('')
    const error = ref<string | null>(null)

    const checkBackend = async () => {
        try {
            const result: any = await checkHealth()
            backendStatus.value = result.status === 'ok' ? 'healthy' : 'unhealthy'
        } catch {
            backendStatus.value = 'unhealthy'
        }
    }

    const learn = async (topic: string, question?: string) => {
        isLoading.value = true
        error.value = null
        currentContent.value = ''
        try {
            const result: any = await quickTeach(topic, question)
            currentContent.value = result.content || ''
        } catch (e: any) {
            error.value = e.message || '请求失败'
        } finally {
            isLoading.value = false
        }
    }

    const practice = async (
        topic: string,
        difficulty: 'easy' | 'medium' | 'hard' = 'medium',
        count = 5
    ) => {
        isLoading.value = true
        error.value = null
        currentPractice.value = ''
        try {
            const result: any = await generatePractice(topic, difficulty, count)
            currentPractice.value = result.content || result.questions || ''
        } catch (e: any) {
            error.value = e.message || '请求失败'
        } finally {
            isLoading.value = false
        }
    }

    return {
        isLoading, backendStatus, currentContent, currentPractice, error,
        checkBackend, learn, practice
    }
})
