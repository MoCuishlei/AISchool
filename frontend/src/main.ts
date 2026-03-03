import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/main.scss'
import './styles/katex-fix.scss'
import 'highlight.js/styles/github-dark.css'

// Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 创建应用
const app = createApp(App)
const pinia = createPinia()

// 注册所有 Element Plus 图标（全局）
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 挂载应用
app.mount('#app')

console.log(`🎓 AI School Frontend | API: ${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}`)