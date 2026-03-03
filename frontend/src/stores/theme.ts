import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
    const theme = ref<'light' | 'dark' | 'auto'>(
        (localStorage.getItem('theme') as 'light' | 'dark' | 'auto') || 'light'
    )

    const setTheme = (t: 'light' | 'dark' | 'auto') => {
        theme.value = t
        localStorage.setItem('theme', t)
        document.documentElement.setAttribute('data-theme', t)
    }

    const toggleTheme = () => {
        setTheme(theme.value === 'light' ? 'dark' : 'light')
    }

    return { theme, setTheme, toggleTheme }
})
