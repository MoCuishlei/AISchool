<template>
  <div class="syllabus">
    <div class="page-header">
      <h2>📋 学习大纲</h2>
      <p>AI 生成系统化课程大纲，点击知识点直接上课或练习，三色标记掌握进度</p>
    </div>

    <!-- 输入区 -->
    <div class="input-section">
      <el-form @submit.prevent="handleGenerate">
        <div class="input-row">
          <el-input
            v-model="topic"
            placeholder="输入学习主题，例如：Python、机器学习、数据结构..."
            size="large"
            clearable
            :disabled="isLoading"
          >
            <template #prefix><el-icon><Reading /></el-icon></template>
          </el-input>
          <el-button type="primary" size="large" native-type="submit"
            :loading="isLoading" :disabled="!topic.trim()" class="gen-btn">
            {{ isLoading ? '生成中...' : '📐 生成课程大纲' }}
          </el-button>
        </div>
        <div class="quick-topics">
          <span class="quick-label">热门课程：</span>
          <el-tag v-for="t in quickTopics" :key="t" style="cursor:pointer" class="quick-tag" @click="topic = t">{{ t }}</el-tag>
        </div>
      </el-form>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error = ''" />

    <div v-if="isLoading" class="loading-state">
      <el-icon class="spin" style="font-size:40px;color:#8b5cf6"><Loading /></el-icon>
      <p>AI 课程规划师正在制定大纲（约 15 秒）...</p>
    </div>

    <!-- 图例 + 统计 -->
    <div v-if="syllabus" class="legend-bar">
      <div class="legend-left">
        <span class="legend-title">掌握程度：</span>
        <span v-for="s in statusList" :key="s.value" class="legend-item">
          <span class="dot" :style="{background: s.color}"></span>{{ s.label }}
        </span>
      </div>
      <div class="legend-right">
        <span class="total-stat">
          总进度：<strong>{{ totalDone }}/{{ totalItems }}</strong> 已掌握
        </span>
        <el-button size="small" @click="resetAll">重置进度</el-button>
      </div>
    </div>

    <!-- 课程大纲 -->
    <div v-if="syllabus" class="outline-wrap">

      <div class="topic-header">
        <div class="topic-meta">
          <span class="course-badge">🎓 课程</span>
          <h3>{{ syllabus.topic }}</h3>
        </div>
        <p>{{ syllabus.description }}</p>
        <!-- 整体进度条 -->
        <div class="overall-progress">
          <div class="overall-bar">
            <div class="overall-fill" :style="{width: overallPct + '%'}" />
          </div>
          <span>{{ overallPct }}% 完成</span>
        </div>
      </div>

      <div v-for="section in syllabus.sections" :key="section.id" class="section-card">
        <div class="section-header">
          <span class="section-num">{{ section.id }}</span>
          <div class="section-info">
            <span class="section-title">{{ section.title }}</span>
            <span class="section-desc">{{ section.description }}</span>
          </div>
          <div class="section-actions">
            <el-button size="small" type="primary" plain @click="learnSection(section.title)">
              <el-icon><Lightning /></el-icon> 学本章
            </el-button>
          </div>
          <div class="section-progress-wrap">
            <span class="progress-text">{{ sectionProgress(section) }}</span>
            <div class="progress-bar">
              <div class="progress-fill" :style="{width: sectionProgressPct(section) + '%'}" />
            </div>
          </div>
        </div>

        <div class="items-grid">
          <div
            v-for="item in section.items"
            :key="item.id"
            class="item-card"
            :class="`item--${getStatus(section.id, item.id)}`"
          >
            <!-- 状态圆 + 内容（点击切换状态）-->
            <div class="item-main" @click="cycleStatus(section.id, item.id)">
              <div class="item-status-dot">
                <span class="status-ring"></span>
              </div>
              <div class="item-content">
                <div class="item-title">{{ item.title }}</div>
                <div class="item-desc">{{ item.description }}</div>
              </div>
              <el-tooltip :content="statusLabel(section.id, item.id)" placement="top">
                <span class="item-badge">{{ statusEmoji(section.id, item.id) }}</span>
              </el-tooltip>
            </div>
            <!-- 快捷操作 -->
            <div class="item-actions">
              <el-button size="small" link type="primary" @click="goLearn(item.title)">
                <el-icon><Lightning /></el-icon> 上课
              </el-button>
              <el-button size="small" link type="success" @click="goPractice(item.title)">
                <el-icon><EditPen /></el-icon> 练习
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getSyllabus } from '@/api/learning'
import { Reading, Loading, Lightning, EditPen } from '@element-plus/icons-vue'

interface SyllabusItem { id: string; title: string; description: string }
interface SyllabusSection { id: string; title: string; description: string; items: SyllabusItem[] }
interface SyllabusData { topic: string; description: string; sections: SyllabusSection[] }

type Status = 'none' | 'learning' | 'done'

const router = useRouter()

const statusList = [
  { value: 'none',     label: '未学习', color: '#f56c6c', emoji: '🔴' },
  { value: 'learning', label: '学习中', color: '#e6a23c', emoji: '🟡' },
  { value: 'done',     label: '已掌握', color: '#67c23a', emoji: '🟢' },
]

const topic = ref('')
const isLoading = ref(false)
const error = ref('')
const syllabus = ref<SyllabusData | null>(null)
const displayTopic = ref('')
const statusMap = ref<Record<string, Status>>({})

const quickTopics = ['Python 编程', '机器学习', '数据结构', 'Vue3 开发', 'SQL 数据库', '计算机网络']

const storageKey = computed(() => `syllabus_status_${displayTopic.value}`)

const totalItems = computed(() => {
  if (!syllabus.value) return 0
  return syllabus.value.sections.reduce((sum, s) => sum + s.items.length, 0)
})

const totalDone = computed(() => {
  if (!syllabus.value) return 0
  return syllabus.value.sections.reduce((sum, section) =>
    sum + section.items.filter(i => getStatus(section.id, i.id) === 'done').length, 0)
})

const overallPct = computed(() =>
  totalItems.value ? Math.round(totalDone.value / totalItems.value * 100) : 0)

function loadStatus() {
  try { statusMap.value = JSON.parse(localStorage.getItem(storageKey.value) || '{}') }
  catch { statusMap.value = {} }
}

function saveStatus() {
  localStorage.setItem(storageKey.value, JSON.stringify(statusMap.value))
}

function getStatus(sId: string, iId: string): Status {
  return statusMap.value[`${sId}-${iId}`] || 'none'
}

function statusLabel(sId: string, iId: string) {
  return statusList.find(x => x.value === getStatus(sId, iId))?.label || '未学习'
}

function statusEmoji(sId: string, iId: string) {
  return statusList.find(x => x.value === getStatus(sId, iId))?.emoji || '🔴'
}

function cycleStatus(sId: string, iId: string) {
  const order: Status[] = ['none', 'learning', 'done']
  const cur = getStatus(sId, iId)
  statusMap.value[`${sId}-${iId}`] = order[(order.indexOf(cur) + 1) % order.length]
  saveStatus()
}

function resetAll() { statusMap.value = {}; saveStatus() }

function sectionProgress(section: SyllabusSection) {
  const done = section.items.filter(i => getStatus(section.id, i.id) === 'done').length
  return `${done}/${section.items.length}`
}

function sectionProgressPct(section: SyllabusSection) {
  const done = section.items.filter(i => getStatus(section.id, i.id) === 'done').length
  return Math.round(done / section.items.length * 100)
}

// 联动跳转
function goLearn(itemTitle: string) {
  router.push({ path: '/learn', query: { topic: `${displayTopic.value} - ${itemTitle}` } })
}

function goPractice(itemTitle: string) {
  router.push({ path: '/practice', query: { topic: `${displayTopic.value} - ${itemTitle}` } })
}

function learnSection(sectionTitle: string) {
  router.push({ path: '/learn', query: { topic: `${displayTopic.value} ${sectionTitle}` } })
}

async function handleGenerate() {
  if (!topic.value.trim()) return
  isLoading.value = true
  error.value = ''
  syllabus.value = null
  displayTopic.value = topic.value
  try {
    const res: any = await getSyllabus(topic.value)
    syllabus.value = res.syllabus || res
    loadStatus()
  } catch (e: any) {
    error.value = e.message || '生成失败，请重试'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.syllabus {
  max-width: 960px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  h2 { font-size: 22px; font-weight: 700; margin: 0 0 6px; }
  p { color: var(--color-text-secondary); margin: 0; font-size: 14px; }
}

.input-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border: 1px solid var(--color-border-lighter);
}

.input-row {
  display: flex; gap: 12px; margin-bottom: 14px;
}

.gen-btn {
  flex-shrink: 0; border-radius: 10px; padding: 0 24px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  border: none;
  &:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(139,92,246,.4); }
}

.quick-topics {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  .quick-label { font-size: 13px; color: var(--color-text-secondary); }
  .quick-tag { cursor: pointer; transition: transform .15s; &:hover { transform: translateY(-1px); } }
}

.loading-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 12px; padding: 40px; color: var(--color-text-secondary);
}
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.legend-bar {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid var(--color-border-lighter);
}

.legend-left { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.legend-title { font-size: 13px; font-weight: 600; color: var(--color-text-secondary); }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 13px; }
.dot { width: 11px; height: 11px; border-radius: 50%; }

.legend-right {
  display: flex; align-items: center; gap: 12px;
  .total-stat { font-size: 13px; color: var(--color-text-secondary); }
}

/* 大纲主体 */
.outline-wrap {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
  border: 1px solid var(--color-border-lighter);
}

.topic-header {
  padding: 24px 28px;
  background: linear-gradient(135deg, #1a1f35 0%, #2d3561 100%);
  color: white;

  .topic-meta {
    display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
    h3 { font-size: 20px; font-weight: 700; margin: 0; }
  }

  .course-badge {
    background: rgba(255,255,255,.15);
    border: 1px solid rgba(255,255,255,.3);
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 12px;
    white-space: nowrap;
  }

  p { font-size: 14px; color: rgba(255,255,255,.75); margin: 0 0 16px; }
}

.overall-progress {
  display: flex; align-items: center; gap: 12px;
  .overall-bar {
    flex: 1; height: 6px; background: rgba(255,255,255,.2);
    border-radius: 3px; overflow: hidden;
    .overall-fill { height: 100%; background: #67c23a; border-radius: 3px; transition: width .4s; }
  }
  span { font-size: 13px; color: rgba(255,255,255,.8); white-space: nowrap; }
}

.section-card {
  background: white;
  border-bottom: 1px solid var(--color-border-lighter);
  &:last-child { border-bottom: none; }
}

.section-header {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 20px;
  background: #fafafa;
  border-bottom: 1px solid var(--color-border-extra-light);
}

.section-num {
  width: 30px; height: 30px; border-radius: 8px; flex-shrink: 0;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white; font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}

.section-info {
  flex: 1;
  .section-title { font-size: 15px; font-weight: 600; display: block; margin-bottom: 2px; }
  .section-desc { font-size: 12px; color: var(--color-text-secondary); }
}

.section-actions { margin-left: auto; }

.section-progress-wrap {
  text-align: right;
  .progress-text { font-size: 12px; color: var(--color-text-secondary); display: block; margin-bottom: 4px; }
  .progress-bar {
    width: 72px; height: 4px; background: #e5e7eb; border-radius: 2px; overflow: hidden;
    .progress-fill { height: 100%; background: #67c23a; transition: width .3s; }
  }
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 8px;
  padding: 12px 16px 16px;
}

.item-card {
  border-radius: 10px; border: 2px solid transparent;
  background: #f8fafc; overflow: hidden;
  transition: all .2s;

  &:hover { box-shadow: 0 2px 10px rgba(0,0,0,.1); }

  &.item--none   { border-color: #fca5a5; background: #fff5f5; .status-ring { background: #f56c6c; } .item-badge { color: #f56c6c; } }
  &.item--learning { border-color: #fcd34d; background: #fffbf0; .status-ring { background: #e6a23c; } .item-badge { color: #e6a23c; } }
  &.item--done   { border-color: #86efac; background: #f0fdf4; .status-ring { background: #67c23a; } .item-badge { color: #67c23a; } }
}

.item-main {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 12px 12px 8px;
  cursor: pointer;
  user-select: none;
}

.item-status-dot {
  flex-shrink: 0; padding-top: 3px;
  .status-ring { width: 13px; height: 13px; border-radius: 50%; display: block; transition: background .2s; }
}

.item-content {
  flex: 1; min-width: 0;
  .item-title { font-size: 13px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 2px; }
  .item-desc { font-size: 11px; color: var(--color-text-secondary); line-height: 1.4; }
}

.item-badge { font-size: 16px; flex-shrink: 0; }

.item-actions {
  display: flex;
  border-top: 1px solid rgba(0,0,0,.06);
  padding: 4px 8px;
  gap: 4px;
}
</style>
