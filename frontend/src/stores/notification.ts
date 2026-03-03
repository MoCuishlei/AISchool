import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Notification } from '@/types/app'

export const useNotificationStore = defineStore('notification', () => {
    const notifications = ref<Notification[]>([])

    const addNotification = (n: Omit<Notification, 'id'>) => {
        const id = Date.now().toString()
        const notification: Notification = { id, duration: 5000, ...n }
        notifications.value.push(notification)

        if (notification.duration && notification.duration > 0) {
            setTimeout(() => removeNotification(id), notification.duration)
        }
    }

    const removeNotification = (id: string) => {
        const idx = notifications.value.findIndex(n => n.id === id)
        if (idx !== -1) notifications.value.splice(idx, 1)
    }

    return { notifications, addNotification, removeNotification }
})
