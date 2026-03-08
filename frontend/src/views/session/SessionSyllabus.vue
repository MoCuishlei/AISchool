<template>
  <div class="session-syllabus">
    <div class="page-header">
      <el-button link @click="$router.push('/my-courses')"><el-icon><ArrowLeft /></el-icon> 课程列表</el-button>
      <div class="header-info">
        <h2>{{ subject }} — 学习大纲</h2>
        <p>点击知识点开始上课，三色标记掌握进度，可任意顺序学习</p>
      </div>
      <div v-if="examUnlock.midterm || examUnlock.has_midterm || examUnlock.final || examUnlock.has_final"
        class="exam-buttons">
        <el-button v-if="examUnlock.midterm" type="warning" @click="goExam('midterm')">
          📑 期中考试（已解锁）
        </el-button>
        <el-button v-if="examUnlock.has_midterm" plain @click="goExam('midterm')">
          📑 期中考试（已考）
        </el-button>
        <el-button v-if="examUnlock.final" type="danger" @click="goExam('final')">
          🎓 期末考试（已解锁）
        </el-button>
      </div>
    </div>

    <!-- 总进度 -->
    <div v-if="items.length" class="overall-card">
      <div class="overall-stats">
        <div class="stat">
          <span class="stat-num text-green">{{ doneCount }}</span>
          <span class="stat-label">已掌握 🟢</span>
        </div>
        <div class="stat">
          <span class="stat-num text-yellow">{{ learningCount }}</span>
          <span class="stat-label">学习中 🟡</span>
        </div>
        <div class="stat">
          <span class="stat-num text-red">{{ noneCount }}</span>
          <span class="stat-label">未学习 🔴</span>
        </div>
        <div class="stat">
          <span class="stat-num">{{ examUnlock.progress }}%</span>
          <span class="stat-label">总进度</span>
        </div>
      </div>
      <div class="overall-bar">
        <div class="segment seg-done" :style="{width: (doneCount/items.length*100) + '%'}" />
        <div class="segment seg-learning" :style="{width: (learningCount/items.length*100) + '%'}" />
      </div>
      <div class="unlock-hint">
        <template v-if="examUnlock.progress < 50">
          还需 {{ Math.ceil((0.5 * items.length) - doneCount) }} 个绿色解锁期中考试
        </template>
        <template v-else-if="examUnlock.progress < 90">
          🎉 期中已解锁！还需更多绿色解锁期末
        </template>
        <template v-else>🎉 期末已解锁！</template>
      </div>
    </div>

    <!-- 加载 -->
    <div v-if="isLoading" class="loading-state">
      <el-icon class="spin"><Loading /></el-icon>
      <p>加载大纲中...</p>
    </div>

    <!-- 大纲 -->
    <div v-if="sections.length" class="outline-wrap">
      <div v-for="sec in sections" :key="sec.section_id" class="section-card">
        <div class="section-header">
          <span class="section-num">{{ sec.section_id }}</span>
          <div class="section-info">
            <span class="section-title">{{ sec.section_title }}</span>
          </div>
          <span class="section-prog">
            {{ sec.items.filter((i: any) => i.status === 'done').length }}/{{ sec.items.length }}
          </span>
        </div>
        <div class="items-list">
          <div v-for="item in sec.items" :key="item.id"
            class="item-row" :class="`item--${item.status}`">
            <div class="item-left" @click="manualToggle(item)">
              <span class="status-dot" />
              <div class="item-text">
                <span class="item-title">{{ item.item_title }}</span>
                <span class="item-desc">{{ item.item_description }}</span>
              </div>
            </div>
            <div class="item-actions">
              <el-tag size="small" :class="`tag--${item.status}`">
                {{ (({ none: '未学', learning: '学习中', done: '已掌握' } as any)[item.status]) }}
              </el-tag>
              <el-button size="small" type="primary" plain @click="goClassroom(item)">
                {{ item.status === 'done' ? '复习' : '上课' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 测验历史（新增） -->
    <div class="quiz-history-section">
      <div class="section-header-row">
        <h3>🕰️ 全局测验记录</h3>
        <el-button link @click="fetchHistory" :loading="loadingHistory">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>

      <div v-if="loadingHistory && !quizHistoryList.length" class="loading-history">
        <el-icon class="spin"><Loading /></el-icon> 正在加载记录...
      </div>
      <div v-else-if="!quizHistoryList.length" class="empty-history">
        暂无任何测验记录，去上课并完成测验吧！
      </div>
      <div v-else class="history-grid">
        <div v-for="q in quizHistoryList" :key="q.id" class="history-item-card" :class="q.passed ? 'passed' : 'failed'">
          <div class="hi-header">
            <span class="hi-tag" :class="q.type">{{ q.type === 'assessment' ? '诊断' : '测验' }}</span>
            <span class="hi-title">{{ q.item_title }}</span>
          </div>
          <div class="hi-body">
            <div class="hi-score">{{ q.score }}分</div>
            <div class="hi-status">{{ q.passed ? '✅ 已通过' : '❌ 未通过' }}</div>
          </div>
          <div class="hi-footer">
            <span class="hi-date">{{ formatDate(q.created_at) }}</span>
            <el-button size="small" link @click="viewQuizDetail(q)">详情</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog v-model="showDetail" :title="`测验详情 - ${currentQuiz?.item_title}`" width="600px" destroy-on-close>
      <div v-if="currentQuiz" class="quiz-detail">
        <div v-for="(question, idx) in currentQuiz.questions" :key="idx" class="detail-item">
          <!-- 题目状态头 -->
          <div v-if="currentQuiz.question_results?.[idx]" class="det-status-row">
            <el-tag size="small" :type="currentQuiz.question_results[idx]?.is_correct ? 'success' : 'danger'">
              {{ currentQuiz.question_results[idx]?.is_correct ? '正确' : '待提升' }}
            </el-tag>
            <span class="det-score">{{ currentQuiz.question_results[idx]?.score }}分</span>
          </div>

          <div class="det-q">问：{{ question.question || question }}</div>
          <div class="det-a">答：{{ currentQuiz.answers?.[idx] }}</div>
          
          <!-- 解析与反馈 -->
          <div v-if="currentQuiz.question_results?.[idx]?.feedback" class="det-f">
            📝 点评：{{ currentQuiz.question_results[idx]?.feedback }}
          </div>
          <div v-if="currentQuiz.question_results?.[idx]?.explanation || question.explanation" class="det-e">
            💡 解析：{{ currentQuiz.question_results?.[idx]?.explanation || question.explanation }}
          </div>
        </div>
        <div class="det-feedback">
          <strong>老师点评：</strong>
          <div v-html="renderMd(currentQuiz.ai_feedback || '暂无评价')" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSession, updateSyllabusItem, checkExamUnlock, getSessionQuizzes } from '@/api/learning'
import { ArrowLeft, Loading, Refresh } from '@element-plus/icons-vue'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()
const sessionId = Number(route.params.sessionId)

const subject = ref('')
const items = ref<any[]>([])
const examUnlock = ref<any>({ midterm: false, final: false, progress: 0 })
const isLoading = ref(false)

// 测验历史相关
const quizHistoryList = ref<any[]>([])
const loadingHistory = ref(false)
const showDetail = ref(false)
const currentQuiz = ref<any>(null)

const renderMd = (text: string) => marked.parse(text)
const formatDate = (ds: string) => {
  if (!ds) return ''
  const d = new Date(ds)
  return `${d.getMonth()+1}-${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

const sections = computed(() => {
  const map: Record<string, any> = {}
  for (const item of items.value) {
    if (!map[item.section_id]) map[item.section_id] = {
      section_id: item.section_id, section_title: item.section_title, items: []
    }
    map[item.section_id].items.push(item)
  }
  return Object.values(map)
})

const doneCount = computed(() => items.value.filter(i => i.status === 'done').length)
const learningCount = computed(() => items.value.filter(i => i.status === 'learning').length)
const noneCount = computed(() => items.value.filter(i => i.status === 'none').length)

onMounted(async () => {
  isLoading.value = true
  try {
    const s: any = await getSession(sessionId)
    subject.value = s.subject
    items.value = s.syllabus_items || []
    examUnlock.value = s.exam_unlock || {}
  } catch {} finally { isLoading.value = false }
})

async function manualToggle(item: any) {
  const order = ['none', 'learning', 'done']
  const next = order[(order.indexOf(item.status) + 1) % order.length]
  item.status = next
  try {
    await updateSyllabusItem(item.id, next)
    const unlock: any = await checkExamUnlock(sessionId)
    examUnlock.value = unlock
  } catch {}
}

function goClassroom(item: any) {
  router.push(`/session/${sessionId}/classroom/${item.id}`)
}

function goExam(type: string) {
  router.push(`/session/${sessionId}/exam/${type}`)
}

async function fetchHistory() {
  loadingHistory.value = true
  try {
    const res: any = await getSessionQuizzes(sessionId)
    quizHistoryList.value = res.quizzes || []
  } catch (e) {
    console.error('Fetch history error:', e)
  } finally {
    loadingHistory.value = false
  }
}

function viewQuizDetail(q: any) {
  currentQuiz.value = q
  showDetail.value = true
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped lang="scss">
.session-syllabus { max-width: 880px; display: flex; flex-direction: column; gap: 16px; }

.page-header {
  display: flex; align-items: flex-start; gap: 16px; flex-wrap: wrap;
  .header-info { flex: 1; h2 { font-size: 20px; font-weight: 800; margin: 0 0 4px; } p { font-size: 13px; color: var(--color-text-secondary); margin: 0; } }
}

.exam-buttons { display: flex; gap: 8px; flex-shrink: 0; }

.overall-card {
  background: white; border-radius: 16px; padding: 20px 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,.06);
}

.overall-stats { display: flex; gap: 32px; margin-bottom: 12px; }
.stat { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.stat-num { font-size: 26px; font-weight: 800; }
.stat-label { font-size: 12px; color: var(--color-text-secondary); }
.text-green { color: #67c23a; }
.text-yellow { color: #e6a23c; }
.text-red { color: #f56c6c; }

.overall-bar {
  height: 8px; background: #f3f4f6; border-radius: 4px; overflow: hidden;
  display: flex; margin-bottom: 8px;
  .segment { height: 100%; transition: width .4s; }
  .seg-done { background: #67c23a; }
  .seg-learning { background: #e6a23c; }
}

.unlock-hint { font-size: 13px; color: var(--color-text-secondary); }

.loading-state { display: flex; flex-direction: column; align-items: center; padding: 40px; gap: 10px; }
.spin { animation: spin 1s linear infinite; color: #8b5cf6; font-size: 36px; }
@keyframes spin { to { transform: rotate(360deg); } }

.outline-wrap { display: flex; flex-direction: column; gap: 10px; }

.section-card {
  background: white; border-radius: 14px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.05);
}

.section-header {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 18px; background: #f8fafc;
  border-bottom: 1px solid var(--color-border-lighter);
}

.section-num {
  width: 28px; height: 28px; border-radius: 7px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white; font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}

.section-info { flex: 1; .section-title { font-size: 14px; font-weight: 700; } }
.section-prog { font-size: 12px; color: var(--color-text-secondary); }

.items-list { padding: 6px 0; }

.item-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 18px; border-bottom: 1px solid var(--color-border-extra-light);
  transition: background .15s;
  &:last-child { border-bottom: none; }

  &.item--none { .status-dot { background: #f56c6c; } }
  &.item--learning { background: #fffbf0; .status-dot { background: #e6a23c; } }
  &.item--done { background: #f0fdf4; .status-dot { background: #67c23a; } }
}

.item-left {
  display: flex; align-items: center; gap: 10px;
  flex: 1; cursor: pointer;
  &:hover { .item-title { color: #8b5cf6; } }
}

.status-dot {
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; transition: background .2s;
}

.item-text { .item-title { font-size: 14px; font-weight: 600; display: block; margin-bottom: 2px; color: var(--color-text-primary); transition: color .15s; } .item-desc { font-size: 12px; color: var(--color-text-secondary); } }

.item-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }

.tag--none { background: #fef0f0 !important; color: #f56c6c !important; border-color: #fca5a5 !important; }
.tag--learning { background: #fdf6ec !important; color: #e6a23c !important; border-color: #fcd34d !important; }
.tag--done { background: #f0f9eb !important; color: #67c23a !important; border-color: #86efac !important; }

/* 测验历史样式 */
.quiz-history-section {
  margin-top: 24px;
  background: white; border-radius: 16px; padding: 20px 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,.05);
  border: 1px solid var(--color-border-lighter);
}
.section-header-row {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;
  h3 { font-size: 17px; font-weight: 700; margin: 0; color: #1e293b; }
}
.loading-history, .empty-history {
  padding: 40px; text-align: center; color: #94a3b8; font-size: 14px;
}
.history-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px;
}
.history-item-card {
  border-radius: 12px; border: 1px solid #e2e8f0; padding: 14px;
  transition: all .2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex; flex-direction: column; gap: 8px;
  background: #fcfdfe;
  &:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.05); }
  &.passed { border-left: 4px solid #10b981; }
  &.failed { border-left: 4px solid #ef4444; }
}
.hi-header {
  display: flex; align-items: center; gap: 8px;
  .hi-tag { font-size: 10px; padding: 1px 6px; border-radius: 4px; font-weight: 600; text-transform: uppercase; }
  .hi-tag.assessment { background: #dbeafe; color: #1e40af; }
  .hi-tag.quiz { background: #fef3c7; color: #92400e; }
  .hi-title { font-size: 13px; font-weight: 600; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
}
.hi-body {
  display: flex; justify-content: space-between; align-items: center;
  .hi-score { font-size: 20px; font-weight: 800; color: #1e293b; }
  .hi-status { font-size: 12px; font-weight: 500; }
}
.hi-footer {
  display: flex; justify-content: space-between; align-items: center;
  border-top: 1px solid #f1f5f9; padding-top: 8px; margin-top: 4px;
  .hi-date { font-size: 11px; color: #94a3b8; }
}

.quiz-detail {
  display: flex; flex-direction: column; gap: 16px;
  .detail-item {
    background: #f8fafc; border-radius: 8px; padding: 12px; margin-bottom: 12px;
    .det-status-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .det-score { font-size: 13px; font-weight: 700; color: #64748b; }
    .det-q { font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 6px; }
    .det-a { font-size: 14px; color: #475569; border-left: 2px solid #cbd5e1; padding-left: 10px; margin-bottom: 8px; }
    .det-f { font-size: 13px; color: #4338ca; background: #e0e7ff; padding: 6px 10px; border-radius: 6px; margin-bottom: 6px; }
    .det-e { font-size: 13px; color: #059669; background: #ecfdf5; padding: 6px 10px; border-radius: 6px; }
  }
  .det-feedback {
    background: #fffbeb; border: 1px solid #fef3c7; border-radius: 8px; padding: 16px;
    font-size: 14px; color: #92400e; line-height: 1.6;
    strong { display: block; margin-bottom: 4px; font-size: 15px; }
  }
}
</style>
