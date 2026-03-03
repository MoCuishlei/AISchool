<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-text">
        <h2>👋 欢迎回来，{{ authStore.user?.name }}</h2>
        <p>开始今天的 AI 辅助学习之旅吧</p>
      </div>
      <div class="backend-status">
        <el-tag
          :type="learningStore.backendStatus === 'healthy' ? 'success' : learningStore.backendStatus === 'unhealthy' ? 'danger' : 'info'"
          size="large"
        >
          <el-icon style="margin-right:4px">
            <CircleCheck v-if="learningStore.backendStatus === 'healthy'" />
            <CircleClose v-else-if="learningStore.backendStatus === 'unhealthy'" />
            <Loading v-else />
          </el-icon>
          AI 后端
          {{ learningStore.backendStatus === 'healthy' ? '运行正常' : learningStore.backendStatus === 'unhealthy' ? '连接失败' : '检测中...' }}
        </el-tag>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card stat-card--blue">
        <el-icon class="stat-icon"><Lightning /></el-icon>
        <div class="stat-info">
          <div class="stat-value">快速学习</div>
          <div class="stat-label">输入主题，AI 立即讲解</div>
        </div>
      </div>
      <div class="stat-card stat-card--green">
        <el-icon class="stat-icon"><EditPen /></el-icon>
        <div class="stat-info">
          <div class="stat-value">练习题</div>
          <div class="stat-label">AI 自动生成，检验掌握程度</div>
        </div>
      </div>
      <div class="stat-card stat-card--purple">
        <el-icon class="stat-icon"><Reading /></el-icon>
        <div class="stat-info">
          <div class="stat-value">多Agent系统</div>
          <div class="stat-label">5个专业AI协作辅导</div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h3 class="section-title">快速开始</h3>
      <div class="action-cards">
        <router-link to="/learn" class="action-card action-card--primary">
          <el-icon class="action-icon"><Lightning /></el-icon>
          <div>
            <div class="action-title">快速学习</div>
            <div class="action-desc">输入任意学习主题，AI 立刻生成讲解内容</div>
          </div>
          <el-icon class="action-arrow"><ArrowRight /></el-icon>
        </router-link>

        <router-link to="/practice" class="action-card action-card--success">
          <el-icon class="action-icon"><EditPen /></el-icon>
          <div>
            <div class="action-title">生成练习题</div>
            <div class="action-desc">选择主题和难度，AI 自动出题帮你巩固</div>
          </div>
          <el-icon class="action-arrow"><ArrowRight /></el-icon>
        </router-link>
      </div>
    </div>

    <!-- API 端点信息 -->
    <div class="api-info">
      <h3 class="section-title">后端 API 信息</h3>
      <div class="api-cards">
        <div class="api-card">
          <code>GET /health</code>
          <span>健康检查</span>
          <el-tag size="small" type="success">GET</el-tag>
        </div>
        <div class="api-card">
          <code>POST /learning/quick-teach</code>
          <span>快速教学</span>
          <el-tag size="small" type="warning">POST</el-tag>
        </div>
        <div class="api-card">
          <code>POST /learning/practice</code>
          <span>生成练习题</span>
          <el-tag size="small" type="warning">POST</el-tag>
        </div>
        <div class="api-card">
          <code>POST /learning/session</code>
          <span>创建学习会话</span>
          <el-tag size="small" type="warning">POST</el-tag>
        </div>
      </div>
      <el-button
        type="primary"
        link
        @click="openDocs"
      >
        查看完整 API 文档 (Swagger) →
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useLearningStore } from '@/stores/learning'
import {
  Lightning, EditPen, Reading, ArrowRight,
  CircleCheck, CircleClose, Loading
} from '@element-plus/icons-vue'

const authStore = useAuthStore()
const learningStore = useLearningStore()

onMounted(() => {
  learningStore.checkBackend()
})

const openDocs = () => {
  window.open('http://localhost:8000/docs', '_blank')
}
</script>

<style scoped lang="scss">
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1000px;
}

.welcome-banner {
  background: linear-gradient(135deg, #1a1f35 0%, #2d3561 100%);
  border-radius: 16px;
  padding: 28px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;

  h2 { margin: 0 0 8px; font-size: 22px; }
  p { margin: 0; color: rgba(255,255,255,0.7); font-size: 14px; }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid var(--color-border-lighter);

  .stat-icon {
    font-size: 36px;
    padding: 12px;
    border-radius: 12px;
  }

  .stat-value { font-size: 16px; font-weight: 700; color: var(--color-text-primary); }
  .stat-label { font-size: 12px; color: var(--color-text-secondary); margin-top: 2px; }

  &--blue .stat-icon { color: #3b82f6; background: #eff6ff; }
  &--green .stat-icon { color: #10b981; background: #ecfdf5; }
  &--purple .stat-icon { color: #8b5cf6; background: #f5f3ff; }
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 16px;
}

.action-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-radius: 12px;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;

  .action-icon {
    font-size: 28px;
    padding: 10px;
    border-radius: 10px;
    flex-shrink: 0;
  }

  .action-title {
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 4px;
  }

  .action-desc {
    font-size: 13px;
    opacity: 0.8;
  }

  .action-arrow {
    margin-left: auto;
    font-size: 18px;
    flex-shrink: 0;
    transition: transform 0.2s;
  }

  &:hover .action-arrow {
    transform: translateX(4px);
  }

  &--primary {
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    color: #1d4ed8;
    .action-icon { color: #3b82f6; background: white; }
    &:hover { border-color: #3b82f6; }
  }

  &--success {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    color: #166534;
    .action-icon { color: #10b981; background: white; }
    &:hover { border-color: #10b981; }
  }
}

.api-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.api-card {
  background: #f8fafc;
  border: 1px solid var(--color-border-lighter);
  border-radius: 8px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 12px;

  code {
    font-family: 'Fira Code', monospace;
    font-size: 13px;
    color: #2563eb;
    min-width: 240px;
  }

  span {
    flex: 1;
    font-size: 13px;
    color: var(--color-text-secondary);
  }
}
</style>
