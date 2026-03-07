<template>
  <div class="main-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed, 'mobile-hidden': !sidebarMobileVisible }">
      <div class="sidebar-header">
        <el-icon class="logo-icon"><Reading /></el-icon>
        <span v-if="!sidebarCollapsed" class="logo-text">AI School</span>
        <el-button class="mobile-close" circle @click="sidebarMobileVisible = false">
          <el-icon><CircleClose /></el-icon>
        </el-button>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="nav-item--active"
          @click="sidebarMobileVisible = false"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <div v-if="!sidebarCollapsed" class="nav-info">
            <span class="nav-label">{{ item.label }}</span>
            <span class="nav-sub">{{ (item as any).sub }}</span>
          </div>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="progress-widget" v-if="!sidebarCollapsed">
          <div class="progress-details">
            <span class="progress-label">总进度</span>
            <span class="progress-value">{{ overallProgress }}%</span>
          </div>
          <el-progress 
            :percentage="overallProgress" 
            :stroke-width="6" 
            :show-text="false"
            color="rgba(255,255,255,0.6)"
            class="custom-progress"
          />
        </div>
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon><component :is="sidebarCollapsed ? 'Expand' : 'Fold'" /></el-icon>
        </button>
      </div>
    </aside>

    <!-- 遮罩层 (Mobile) -->
    <div v-if="sidebarMobileVisible" class="sidebar-overlay" @click="sidebarMobileVisible = false"></div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部 Header -->
      <header class="topbar">
        <div class="topbar-left">
          <el-button class="mobile-menu-btn" circle @click="sidebarMobileVisible = true">
            <el-icon><Fold /></el-icon>
          </el-button>
          <h1 class="page-title">{{ currentTitle }}</h1>
        </div>
        <div class="topbar-right">
          <el-tag
            :type="backendHealthy ? 'success' : 'danger'"
            size="small"
            class="status-tag hide-mobile"
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
          <span class="user-name hide-mobile">{{ authStore.user?.name }}</span>
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
  Fold, Expand, CircleCheck, CircleClose, Sunny, Moon, School, List,
  Setting, Document
} from '@element-plus/icons-vue'

import { getStudentSessions } from '@/api/learning'

const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const learningStore = useLearningStore()

const sidebarCollapsed = ref(false)
const sidebarMobileVisible = ref(false)
const sessions = ref<any[]>([])

const navItems = [
  { path: '/my-courses', label: '学习中心', icon: 'School', sub: 'Study Hub' },
  { path: '/dashboard', label: '学情看板', icon: 'Odometer', sub: 'Analytics' },
  { path: '/syllabus', label: '学习大纲', icon: 'List', sub: 'Syllabus' },
  { path: '/practice', label: '探索练习', icon: 'EditPen', sub: 'Practice' },
  { path: '/settings/config', label: '模型配置', icon: 'Setting', sub: 'LLM Config' },
  { path: '/docs/api', label: 'API 文档', icon: 'Document', sub: 'Docs' },
]

const currentTitle = computed(() => {
  const found = navItems.find(n => route.path.startsWith(n.path))
  return found?.label || 'AI School'
})

const backendHealthy = computed(() => learningStore.backendStatus === 'healthy')

const overallProgress = computed(() => {
  if (sessions.value.length === 0) return 0
  const sum = sessions.value.reduce((acc, s) => acc + (s.progress_pct || 0), 0)
  return Math.round(sum / sessions.value.length)
})

onMounted(async () => {
  learningStore.checkBackend()
  try {
    const res: any = await getStudentSessions(authStore.user?.name || '学习者')
    sessions.value = res.sessions || []
  } catch (e) {
    console.error('Failed to fetch sessions for progress:', e)
  }
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
  width: 240px;
  background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  box-shadow: 4px 0 20px rgba(0,0,0,0.3);
  z-index: 2000;

  &.collapsed {
    width: 72px;
  }

  @media (max-width: 768px) {
    position: fixed;
    height: 100vh;
    left: 0;
    top: 0;
    width: 280px !important;
    transform: translateX(0);
    
    &.mobile-hidden {
      transform: translateX(-100%);
    }
    
    &.collapsed {
      width: 280px !important;
    }
  }
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.05);

  .mobile-close {
    display: none;
    margin-left: auto;
    background: transparent !important;
    border: none !important;
    color: white !important;
    font-size: 20px;
    @media (max-width: 768px) { display: flex; }
  }

  .logo-icon {
    font-size: 28px;
    color: #818cf8;
    filter: drop-shadow(0 0 8px rgba(129, 140, 248, 0.5));
  }

  .logo-text {
    font-size: 20px;
    font-weight: 800;
    color: white;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
}

.sidebar-nav {
  flex: 1;
  padding: 20px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;

  .el-icon {
    font-size: 20px;
    transition: transform 0.25s ease;
  }

  .nav-info {
    display: flex;
    flex-direction: column;
    .nav-label { font-size: 14px; font-weight: 600; }
    .nav-sub { font-size: 10px; opacity: 0.5; font-weight: 400; text-transform: uppercase; }
  }

  &:hover {
    background: rgba(255,255,255,0.08);
    color: white;
    .el-icon { transform: scale(1.1); }
  }

  &--active {
    background: linear-gradient(90deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.05) 100%);
    color: #818cf8;
    box-shadow: inset 0 0 0 1px rgba(99, 102, 241, 0.3);
    
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 20%;
      bottom: 20%;
      width: 4px;
      background: #818cf8;
      border-radius: 0 4px 4px 0;
      box-shadow: 0 0 10px #818cf8;
    }
  }
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255,255,255,0.05);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-widget {
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  padding: 12px;
  .pw-info {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: rgba(255,255,255,0.5);
    margin-bottom: 6px;
  }
  :deep(.el-progress-bar__outer) { background-color: rgba(255,255,255,0.1); }
}

.collapse-btn {
  align-self: center;
  background: rgba(255,255,255,0.05);
  border: none;
  color: rgba(255,255,255,0.4);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  justify-content: center;
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
  position: relative;
}

.topbar {
  height: 64px;
  background: rgba(255,255,255,0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border-lighter);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  flex-shrink: 0;
  z-index: 90;

  @media (max-width: 768px) {
    padding: 0 16px;
  }

  .theme-dark & {
    background: rgba(15, 23, 42, 0.8);
    border-bottom-color: rgba(255,255,255,0.05);
  }
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;

  .mobile-menu-btn {
    display: none;
    @media (max-width: 768px) { display: flex; }
  }

  .page-title {
    font-size: 20px;
    font-weight: 700;
    color: var(--color-text-primary);
    letter-spacing: -0.5px;
    
    @media (max-width: 576px) { font-size: 16px; }
  }
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
  
  @media (max-width: 768px) { gap: 10px; }
}

.hide-mobile {
  @media (max-width: 768px) { display: none !important; }
}

.status-tag {
  border: none;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  font-weight: 500;
}

.user-avatar {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #f8fafc;
  
  @media (max-width: 768px) {
    padding: 16px 12px;
  }
  
  .theme-dark & { background: #0f172a; }
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
