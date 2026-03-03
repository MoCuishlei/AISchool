<template>
  <div class="main-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <el-icon class="logo-icon"><Reading /></el-icon>
        <span v-if="!sidebarCollapsed" class="logo-text">AI School</span>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="nav-item--active"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span v-if="!sidebarCollapsed" class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon><component :is="sidebarCollapsed ? 'Expand' : 'Fold'" /></el-icon>
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部 Header -->
      <header class="topbar">
        <div class="topbar-left">
          <h1 class="page-title">{{ currentTitle }}</h1>
        </div>
        <div class="topbar-right">
          <el-tag
            :type="backendHealthy ? 'success' : 'danger'"
            size="small"
            class="status-tag"
          >
            <el-icon><CircleCheck v-if="backendHealthy" /><CircleClose v-else /></el-icon>
            后端 {{ backendHealthy ? '正常' : '离线' }}
          </el-tag>
          <el-button
            :icon="themeStore.theme === 'dark' ? Sunny : Moon"
            circle
            size="small"
            @click="themeStore.toggleTheme()"
          />
          <el-avatar :size="32" class="user-avatar">
            {{ authStore.user?.name?.charAt(0) }}
          </el-avatar>
          <span class="user-name">{{ authStore.user?.name }}</span>
        </div>
      </header>

      <!-- 路由内容 -->
      <main class="content-area">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useLearningStore } from '@/stores/learning'
import {
  Reading, Odometer, Lightning, EditPen,
  Fold, Expand, CircleCheck, CircleClose, Sunny, Moon
} from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const learningStore = useLearningStore()

const sidebarCollapsed = ref(false)

const navItems = [
  { path: '/my-courses', label: '我的课堂', icon: 'School' },
  { path: '/dashboard', label: '仪表盘', icon: 'Odometer' },
  { path: '/learn', label: '快速学习', icon: 'Lightning' },
  { path: '/syllabus', label: '学习大纲', icon: 'List' },
  { path: '/practice', label: '练习题', icon: 'EditPen' },
]

const currentTitle = computed(() => {
  const found = navItems.find(n => route.path.startsWith(n.path))
  return found?.label || 'AI School'
})

const backendHealthy = computed(() => learningStore.backendStatus === 'healthy')

onMounted(() => {
  learningStore.checkBackend()
})
</script>

<style scoped lang="scss">
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--color-bg-base);
}

.sidebar {
  width: 220px;
  background: linear-gradient(180deg, #1a1f35 0%, #2d3561 100%);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  flex-shrink: 0;
  box-shadow: 4px 0 12px rgba(0,0,0,0.15);

  &.collapsed {
    width: 64px;
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.1);

  .logo-icon {
    font-size: 24px;
    color: #60a5fa;
    flex-shrink: 0;
  }

  .logo-text {
    font-size: 18px;
    font-weight: 700;
    color: white;
    white-space: nowrap;
  }
}

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  transition: all 0.2s;
  white-space: nowrap;
  overflow: hidden;

  .el-icon {
    font-size: 18px;
    flex-shrink: 0;
  }

  .nav-label {
    font-size: 14px;
  }

  &:hover {
    background: rgba(255,255,255,0.1);
    color: white;
    text-decoration: none;
  }

  &--active {
    background: rgba(96, 165, 250, 0.2);
    color: #60a5fa;
    font-weight: 600;
  }
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.collapse-btn {
  width: 100%;
  background: none;
  border: none;
  color: rgba(255,255,255,0.6);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  font-size: 16px;
  transition: all 0.2s;

  &:hover {
    background: rgba(255,255,255,0.1);
    color: white;
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.topbar {
  height: 60px;
  background: white;
  border-bottom: 1px solid var(--color-border-lighter);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);

  .theme-dark & {
    background: #1d1e1f;
    border-bottom-color: #363637;
  }
}

.topbar-left {
  .page-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
  }
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: default;
}

.user-avatar {
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.user-name {
  font-size: 14px;
  color: var(--color-text-regular);
  font-weight: 500;
}

.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
