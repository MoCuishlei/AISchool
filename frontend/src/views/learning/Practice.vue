<template>
  <div class="practice">
    <div class="page-header">
      <h2>✏️ 练习题生成</h2>
      <p>选择主题和难度，AI 自动生成练习题帮你巩固知识</p>
    </div>

    <!-- 配置区 -->
    <div class="config-section">
      <el-form label-position="top">
        <div class="form-row">
          <el-form-item label="学习主题" class="flex-2">
            <el-input
              v-model="topic"
              placeholder="例如：Python 基础语法、数据库索引优化..."
              size="large"
              clearable
              :disabled="learningStore.isLoading"
            />
          </el-form-item>

          <el-form-item label="难度">
            <el-select v-model="difficulty" size="large" style="width:140px">
              <el-option label="🟢 简单" value="easy" />
              <el-option label="🟡 中等" value="medium" />
              <el-option label="🔴 困难" value="hard" />
            </el-select>
          </el-form-item>

          <el-form-item label="题目数量">
            <el-input-number
              v-model="count"
              :min="1"
              :max="10"
              size="large"
              style="width:120px"
            />
          </el-form-item>
        </div>

        <div class="quick-topics">
          <span class="quick-label">热门主题：</span>
          <el-tag
            v-for="t in quickTopics"
            :key="t"
            class="quick-tag"
            @click="topic = t"
            style="cursor:pointer"
          >{{ t }}</el-tag>
        </div>

        <el-button
          type="success"
          size="large"
          :loading="learningStore.isLoading"
          :disabled="!topic.trim()"
          class="generate-btn"
          @click="handlePractice"
        >
          <el-icon v-if="!learningStore.isLoading"><EditPen /></el-icon>
          {{ learningStore.isLoading ? 'AI 正在生成题目...' : '生成练习题' }}
        </el-button>
      </el-form>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="learningStore.error"
      :title="learningStore.error"
      type="error"
      show-icon
      closable
    />

    <!-- 加载状态 -->
    <div v-if="learningStore.isLoading" class="loading-state">
      <el-icon class="loading-icon spin"><Loading /></el-icon>
      <p>AI 正在出题，请稍候（通常需要 10-30 秒）...</p>
    </div>

    <!-- 题目展示 -->
    <div v-if="learningStore.currentPractice && !learningStore.isLoading" class="questions-section">
      <div class="questions-header">
        <h3>📝 练习题：{{ displayTopic }}</h3>
        <div class="header-actions">
          <el-tag :type="difficultyColor">{{ difficultyLabel }}</el-tag>
          <el-button size="small" @click="copyContent">
            <el-icon><CopyDocument /></el-icon> 复制
          </el-button>
        </div>
      </div>
      <div class="questions-body" v-html="renderedContent" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLearningStore } from '@/stores/learning'
import { EditPen, Loading, CopyDocument } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const learningStore = useLearningStore()
const topic = ref('')
const difficulty = ref<'easy' | 'medium' | 'hard'>('medium')
const count = ref(5)
const displayTopic = ref('')

// 自动填充来自大纲或学习页的主题
onMounted(() => {
  if (route.query.topic) {
    topic.value = route.query.topic as string
  }
})

const quickTopics = [
  'Python 基础', '数据结构', '算法入门',
  'Vue3 基础', 'SQL 查询', '网络协议'
]

const difficultyLabel = computed(() => ({
  easy: '🟢 简单', medium: '🟡 中等', hard: '🔴 困难'
}[difficulty.value]))

const difficultyColor = computed(() => ({
  easy: 'success', medium: 'warning', hard: 'danger'
}[difficulty.value] as 'success' | 'warning' | 'danger'))

const handlePractice = async () => {
  if (!topic.value.trim()) return
  displayTopic.value = topic.value
  await learningStore.practice(topic.value, difficulty.value, count.value)
}

import { renderMd } from '@/utils/markdown'

const renderedContent = computed(() => {
  return renderMd(learningStore.currentPractice)
})

const copyContent = () => {
  navigator.clipboard.writeText(learningStore.currentPractice)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped lang="scss">
.practice {
  max-width: 860px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  h2 { font-size: 22px; font-weight: 700; margin: 0 0 8px; }
  p { color: var(--color-text-secondary); margin: 0; }
}

.config-section {
  background: white;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border: 1px solid var(--color-border-lighter);
}

.form-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  flex-wrap: wrap;
  margin-bottom: 16px;

  .flex-2 { flex: 2; min-width: 200px; }
}

.quick-topics {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
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

.generate-btn {
  border-radius: 10px;
  padding: 0 28px;
  height: 44px;
  font-size: 15px;
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  &:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(16,185,129,0.4); }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: var(--color-text-secondary);
  .loading-icon { font-size: 40px; color: #10b981; }
}

.spin { animation: spin 1s linear infinite; }

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.questions-section {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border: 1px solid var(--color-border-lighter);
}

.questions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border-lighter);
  background: #f8fafc;

  h3 { margin: 0; font-size: 16px; }
  .header-actions { display: flex; gap: 8px; align-items: center; }
}

.questions-body {
  padding: 24px;
  line-height: 1.8;
  font-size: 15px;
  color: var(--color-text-primary);

  :deep(h1), :deep(h2), :deep(h3) {
    margin: 16px 0 8px;
    color: #059669;
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
  }

  :deep(strong) { color: #065f46; }
}
</style>
