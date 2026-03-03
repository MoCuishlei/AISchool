<template>
  <div class="quick-learn">
    <div class="page-header">
      <h2>⚡ 快速学习</h2>
      <p>输入任意学习主题，AI 将立即为你生成详细的学习内容</p>
    </div>

    <!-- 输入区 -->
    <div class="input-section">
      <el-form @submit.prevent="handleLearn">
        <el-form-item label="学习主题" class="topic-input">
          <el-input
            v-model="topic"
            placeholder="例如：Python 装饰器、机器学习基础、SQL 联表查询..."
            size="large"
            clearable
            :disabled="learningStore.isLoading"
          >
            <template #prefix>
              <el-icon><Reading /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="具体问题（可选）">
          <el-input
            v-model="question"
            type="textarea"
            :rows="2"
            placeholder="有具体不懂的问题？在这里提问，AI 会重点解答"
            :disabled="learningStore.isLoading"
          />
        </el-form-item>

        <div class="action-row">
          <el-button
            type="primary"
            size="large"
            native-type="submit"
            :loading="learningStore.isLoading"
            :disabled="!topic.trim()"
            class="learn-btn"
          >
            <el-icon v-if="!learningStore.isLoading"><Lightning /></el-icon>
            {{ learningStore.isLoading ? 'AI 正在生成内容...' : '开始学习' }}
          </el-button>

          <!-- 快捷主题 -->
          <div class="quick-topics">
            <span class="quick-label">快捷选择：</span>
            <el-tag
              v-for="t in quickTopics"
              :key="t"
              class="quick-tag"
              @click="selectTopic(t)"
              style="cursor:pointer"
            >{{ t }}</el-tag>
          </div>
        </div>
      </el-form>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="learningStore.error"
      :title="learningStore.error"
      type="error"
      show-icon
      closable
      @close="learningStore.error = null"
    />

    <!-- 加载状态 -->
    <div v-if="learningStore.isLoading" class="loading-state">
      <el-icon class="loading-icon spin"><Loading /></el-icon>
      <p>AI 正在思考，请稍候（通常需要 10-30 秒）...</p>
    </div>

    <!-- 学习内容展示 -->
    <div v-if="learningStore.currentContent && !learningStore.isLoading" class="content-section">
      <div class="content-header">
        <h3>📖 {{ displayTopic }}</h3>
        <div class="header-actions">
          <el-button size="small" type="success" @click="goPractice">
            <el-icon><EditPen /></el-icon> 做练习
          </el-button>
          <el-button size="small" @click="copyContent">
            <el-icon><CopyDocument /></el-icon> 复制
          </el-button>
        </div>
      </div>
      <div class="content-body" v-html="renderedContent" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLearningStore } from '@/stores/learning'
import { Lightning, Reading, Loading, CopyDocument, EditPen, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { renderMd } from '@/utils/markdown'

const route = useRoute()
const router = useRouter()
const learningStore = useLearningStore()
const topic = ref('')
const question = ref('')
const displayTopic = ref('')

// 从大纲页面跳转时自动填充主题
onMounted(() => {
  if (route.query.topic) {
    topic.value = route.query.topic as string
  }
})

const quickTopics = [
  'Python 装饰器',
  '机器学习入门',
  'Vue3 组合式API',
  'SQL 联表查询',
  '算法复杂度',
  'REST API 设计'
]

const selectTopic = (t: string) => {
  topic.value = t
}

const handleLearn = async () => {
  if (!topic.value.trim()) return
  displayTopic.value = topic.value
  await learningStore.learn(topic.value, question.value || undefined)
}

// 简单的 Markdown 渲染（保留换行和代码块）
const renderedContent = computed(() => {
  return renderMd(learningStore.currentContent)
})

const copyContent = () => {
  navigator.clipboard.writeText(learningStore.currentContent)
  ElMessage.success('已复制到剪贴板')
}

const goPractice = () => {
  router.push({ path: '/practice', query: { topic: displayTopic.value } })
}
</script>

<style scoped lang="scss">
.quick-learn {
  max-width: 860px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  h2 { font-size: 22px; font-weight: 700; margin: 0 0 8px; }
  p { color: var(--color-text-secondary); margin: 0; }
}

.input-section {
  background: white;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border: 1px solid var(--color-border-lighter);
}

.topic-input {
  :deep(.el-input__wrapper) {
    border-radius: 10px;
  }
}

.action-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.learn-btn {
  border-radius: 10px;
  padding: 0 28px;
  height: 44px;
  font-size: 15px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;

  &:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(59,130,246,0.4); }
}

.quick-topics {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.quick-tag {
  cursor: pointer;
  transition: all 0.2s;
  &:hover { transform: translateY(-1px); }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: var(--color-text-secondary);

  .loading-icon {
    font-size: 40px;
    color: #3b82f6;
  }
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.content-section {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border: 1px solid var(--color-border-lighter);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border-lighter);
  background: #f8fafc;

  h3 { margin: 0; font-size: 16px; }
  .header-actions { display: flex; gap: 8px; }
}

.content-body {
  padding: 24px;
  line-height: 1.8;
  font-size: 15px;
  color: var(--color-text-primary);

  :deep(h1), :deep(h2), :deep(h3) {
    margin: 16px 0 8px;
    color: #1d4ed8;
  }

  :deep(code) {
    background: #f1f5f9;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Fira Code', monospace;
    font-size: 13px;
    color: #d63384;
  }

  :deep(pre) {
    background: #1e293b;
    color: #e2e8f0;
    padding: 16px 20px;
    border-radius: 10px;
    overflow-x: auto;
    margin: 12px 0;

    code {
      background: none;
      padding: 0;
      color: inherit;
      font-size: 14px;
    }
  }

  :deep(strong) {
    color: #1e40af;
  }
}
</style>
