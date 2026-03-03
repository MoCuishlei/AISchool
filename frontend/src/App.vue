<template>
  <div id="app" :class="themeClass">
    <!-- 全局加载状态 -->
    <div v-if="appStore.isLoading" class="global-loading">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 全局错误提示 -->
    <div v-if="appStore.globalError" class="global-error">
      <el-alert
        :title="appStore.globalError.title"
        :description="appStore.globalError.message"
        type="error"
        show-icon
        closable
        @close="appStore.clearGlobalError"
      />
    </div>

    <!-- 路由视图 -->
    <router-view v-slot="{ Component, route }">
      <transition
        :name="route.meta.transition || 'fade'"
        mode="out-in"
        @before-enter="onBeforeEnter"
        @after-enter="onAfterEnter"
      >
        <component :is="Component" :key="route.fullPath" />
      </transition>
    </router-view>

    <!-- 全局通知 -->
    <div class="global-notifications">
      <transition-group name="notification">
        <div
          v-for="notification in notificationStore.notifications"
          :key="notification.id"
          class="notification-item"
          :class="`notification-${notification.type}`"
        >
          <el-icon class="notification-icon">
            <component :is="getNotificationIcon(notification.type)" />
          </el-icon>
          <div class="notification-content">
            <div class="notification-title">{{ notification.title }}</div>
            <div class="notification-message">{{ notification.message }}</div>
          </div>
          <el-icon class="notification-close" @click="removeNotification(notification.id)">
            <Close />
          </el-icon>
        </div>
      </transition-group>
    </div>

    <!-- 回到顶部 -->
    <el-backtop
      v-if="showBackTop"
      :right="20"
      :bottom="80"
      target="#app"
      :visibility-height="300"
    >
      <el-icon><Top /></el-icon>
    </el-backtop>

    <!-- 全局设置面板 -->
    <global-settings v-if="showSettings" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useNotificationStore } from '@/stores/notification'
import { useThemeStore } from '@/stores/theme'
import GlobalSettings from '@/components/layout/GlobalSettings.vue'
import {
  Loading,
  Close,
  Top,
  SuccessFilled,
  WarningFilled,
  InfoFilled,
  CircleCloseFilled
} from '@element-plus/icons-vue'

const route = useRoute()
const appStore = useAppStore()
const notificationStore = useNotificationStore()
const themeStore = useThemeStore()

// 响应式数据
const showBackTop = ref(false)
const showSettings = ref(false)

// 计算属性
const themeClass = computed(() => ({
  'theme-light': themeStore.theme === 'light',
  'theme-dark': themeStore.theme === 'dark',
  'theme-auto': themeStore.theme === 'auto'
}))

// 方法
const getNotificationIcon = (type: string) => {
  const icons: Record<string, any> = {
    success: SuccessFilled,
    warning: WarningFilled,
    info: InfoFilled,
    error: CircleCloseFilled
  }
  return icons[type] || InfoFilled
}

const removeNotification = (id: string) => {
  notificationStore.removeNotification(id)
}

const onBeforeEnter = () => {
  // 页面切换前的处理
  appStore.setLoading(true)
}

const onAfterEnter = () => {
  // 页面切换后的处理
  setTimeout(() => {
    appStore.setLoading(false)
  }, 300)
}

// 滚动处理
const handleScroll = () => {
  showBackTop.value = window.scrollY > 300
}

// 键盘快捷键
const handleKeyDown = (e: KeyboardEvent) => {
  // Ctrl + , 打开设置
  if (e.ctrlKey && e.key === ',') {
    e.preventDefault()
    showSettings.value = !showSettings.value
  }
  
  // Esc 关闭设置
  if (e.key === 'Escape' && showSettings.value) {
    showSettings.value = false
  }
}

// 生命周期
onMounted(() => {
  // 初始化应用
  appStore.initializeApp()
  
  // 监听滚动
  window.addEventListener('scroll', handleScroll)
  
  // 监听键盘事件
  window.addEventListener('keydown', handleKeyDown)
  
  // 检查更新
  if (import.meta.env.PROD) {
    checkForUpdates()
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('keydown', handleKeyDown)
})

// 检查更新
const checkForUpdates = () => {
  const lastUpdateCheck = localStorage.getItem('lastUpdateCheck')
  const now = Date.now()
  
  // 每天检查一次
  if (!lastUpdateCheck || now - parseInt(lastUpdateCheck) > 24 * 60 * 60 * 1000) {
    fetch('/version.json?' + now)
      .then(res => res.json())
      .then(data => {
        const currentVersion = import.meta.env.VITE_APP_VERSION || '1.0.0'
        if (data.version !== currentVersion) {
          notificationStore.addNotification({
            title: '新版本可用',
            message: `检测到新版本 ${data.version}，请刷新页面获取更新`,
            type: 'info',
            duration: 10000,
            action: {
              label: '刷新',
              handler: () => location.reload()
            }
          })
        }
        localStorage.setItem('lastUpdateCheck', now.toString())
      })
      .catch(() => {
        // 静默失败
      })
  }
}
</script>

<style lang="scss" scoped>
#app {
  min-height: 100vh;
  transition: background-color 0.3s, color 0.3s;
  
  &.theme-light {
    background-color: var(--el-bg-color);
    color: var(--el-text-color-primary);
  }
  
  &.theme-dark {
    background-color: var(--el-bg-color-page);
    color: var(--el-text-color-primary);
  }
}

.global-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  
  .loading-icon {
    font-size: 48px;
    color: var(--el-color-primary);
    margin-bottom: 16px;
    animation: spin 1s linear infinite;
  }
  
  span {
    font-size: 16px;
    color: var(--el-text-color-regular);
  }
}

.global-error {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 600px;
  z-index: 9998;
}

.global-notifications {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9997;
  max-width: 400px;
  
  .notification-item {
    display: flex;
    align-items: flex-start;
    padding: 16px;
    margin-bottom: 10px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    background: white;
    animation: slideInRight 0.3s ease;
    
    &.notification-success {
      border-left: 4px solid var(--el-color-success);
    }
    
    &.notification-warning {
      border-left: 4px solid var(--el-color-warning);
    }
    
    &.notification-info {
      border-left: 4px solid var(--el-color-info);
    }
    
    &.notification-error {
      border-left: 4px solid var(--el-color-error);
    }
    
    .notification-icon {
      margin-right: 12px;
      font-size: 20px;
      flex-shrink: 0;
      
      .notification-success & {
        color: var(--el-color-success);
      }
      
      .notification-warning & {
        color: var(--el-color-warning);
      }
      
      .notification-info & {
        color: var(--el-color-info);
      }
      
      .notification-error & {
        color: var(--el-color-error);
      }
    }
    
    .notification-content {
      flex: 1;
      min-width: 0;
      
      .notification-title {
        font-weight: 600;
        margin-bottom: 4px;
        color: var(--el-text-color-primary);
      }
      
      .notification-message {
        font-size: 14px;
        color: var(--el-text-color-regular);
        line-height: 1.4;
      }
    }
    
    .notification-close {
      margin-left: 12px;
      cursor: pointer;
      color: var(--el-text-color-secondary);
      flex-shrink: 0;
      
      &:hover {
        color: var(--el-text-color-primary);
      }
    }
  }
}

// 动画
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

// 页面切换动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

// 通知动画
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from,
.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notification-move {
  transition: transform 0.3s ease;
}

// 响应式
@media (max-width: 768px) {
  .global-notifications {
    left: 10px;
    right: 10px;
    top: 10px;
    max-width: none;
  }
  
  .notification-item {
    padding: 12px;
  }
}
</style>