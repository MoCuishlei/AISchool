import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    timeout: 120000, // 直连 LLM 约 10-30s，留足余量
    headers: {
        'Content-Type': 'application/json'
    }
})


// 请求拦截器
api.interceptors.request.use(
    config => config,
    error => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
    response => response.data,
    error => {
        const message = error.response?.data?.detail || error.message || '请求失败'
        return Promise.reject(new Error(message))
    }
)

export default api
