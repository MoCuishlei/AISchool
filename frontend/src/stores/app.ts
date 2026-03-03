import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AppError } from '@/types/app'

export const useAppStore = defineStore('app', () => {
  // 状态
  const isLoading = ref(false)
  const globalError = ref<AppError | null>(null)
  const isInitialized = ref(false)
  const isOnline = ref(navigator.onLine)
  const appVersion = ref(import.meta.env.VITE_APP_VERSION || '1.0.0')
  
  // 计算属性
  const hasError = computed(() => globalError.value !== null)
  
  // Actions
  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }
  
  const showError = (title: string, message: string, details?: any) => {
    globalError.value = {
      title,
      message,
      details,
      timestamp: Date.now()
    }
    
    // 自动清除错误（可选）
    setTimeout(() => {
      clearGlobalError()
    }, 10000)
  }
  
  const clearGlobalError = () => {
    globalError.value = null
  }
  
  const initializeApp = async () => {
    if (isInitialized.value) return
    
    try {
      setLoading(true)
      
      // 检查网络状态
      window.addEventListener('online', () => {
        isOnline.value = true
      })
      
      window.addEventListener('offline', () => {
        isOnline.value = false
        showError('网络连接已断开', '请检查您的网络连接')
      })
      
      // 检查服务状态
      await checkServiceStatus()
      
      // 加载用户偏好
      await loadUserPreferences()
      
      isInitialized.value = true
    } catch (error) {
      console.error('应用初始化失败:', error)
      showError('应用初始化失败', '请刷新页面重试', error)
    } finally {
      setLoading(false)
    }
  }
  
  const checkServiceStatus = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/health`)
      if (!response.ok) {
        throw new Error('服务不可用')
      }
    } catch (error) {
      console.warn('后端服务检查失败:', error)
      // 不阻止应用启动，但记录警告
    }
  }
  
  const loadUserPreferences = async () => {
    // 从localStorage加载用户偏好
    const theme = localStorage.getItem('theme') || 'light'
    const language = localStorage.getItem('language') || 'zh-CN'
    
    // 应用主题
    document.documentElement.setAttribute('data-theme', theme)
    
    // 可以在这里加载更多用户偏好
  }
  
  const resetApp = () => {
    isLoading.value = false
    globalError.value = null
    isInitialized.value = false
  }
  
  // 导出
  return {
    // 状态
    isLoading,
    globalError,
    isInitialized,
    isOnline,
    appVersion,
    
    // 计算属性
    hasError,
    
    // Actions
    setLoading,
    showError,
    clearGlobalError,
    initializeApp,
    resetApp
  }
})