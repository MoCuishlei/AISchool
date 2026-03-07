<template>
  <div class="classroom">
    <!-- 顶部栏 -->
    <div class="classroom-header">
      <el-button link @click="$router.back()"><el-icon><ArrowLeft /></el-icon> 返回大纲</el-button>
      <div class="header-center">
        <span class="subject-badge">{{ sessionSubject }}</span>
        <span class="item-title">{{ itemTitle }}</span>
      </div>
      <div class="header-right">
        <el-tag :type="phaseTag[phase]" size="small" class="mr-2">{{ phaseLabel[phase] }}</el-tag>
        <el-button type="info" plain size="small" @click="openHistory"><el-icon><Clock /></el-icon> 测验历史</el-button>
      </div>
    </div>

    <!-- 讲课阶段 -->
    <div v-if="phase === 'lesson'" class="lesson-section">
      <div v-if="isLoading" class="loading-state">
        <el-icon class="spin"><Loading /></el-icon>
        <div class="progress-text">{{ lessonLoadingMsgs[lessonLoadingIdx] }}</div>
        <div class="progress-time">已用时 {{ lessonLoadingTime }} 秒</div>
      </div>
      <div v-else class="lesson-card">
        <div class="lesson-content" v-html="renderedContent" />

        <!-- 提问区 -->
        <div class="qa-section">
          <div v-if="qaHistory.length" class="qa-history">
            <!-- 按问答对展示，每对可单独删除 -->
            <div
              v-for="(pair, pairIdx) in qaPairs"
              :key="pairIdx"
              class="qa-pair"
            >
              <!-- 删除按钮 -->
              <button class="qa-delete-btn" @click="deleteQaPair(pairIdx)" title="删除此问答">
                <el-icon><Delete /></el-icon>
              </button>
              <!-- 问 -->
              <div class="qa-msg user">
                <span class="role-badge">你</span>
                <div class="msg-content">{{ pair.question }}</div>
              </div>
              <!-- 答 -->
              <div class="qa-msg assistant">
                <span class="role-badge">老师</span>
                <div class="msg-content" v-html="renderMd(pair.answer)" />
              </div>
            </div>
          </div>
          <div class="qa-input-row">
            <el-input v-model="question" placeholder="有疑问？直接提问..." clearable
              :disabled="isAsking" @keydown.enter.prevent="askQuestion" />
            <el-button type="primary" :loading="isAsking" @click="askQuestion" :disabled="!question.trim()">
              提问
            </el-button>
          </div>
        </div>

        <div class="ready-row">
          <p class="ready-tip">👆 随时提问，觉得掌握了就开始小测验</p>
          <el-button type="success" size="large" @click="startQuiz" :loading="isStartingQuiz">
            ✅ 我学会了，开始小测验
          </el-button>
        </div>
      </div>
    </div>

    <!-- 小测验阶段 -->
    <div v-if="phase === 'quiz'" class="quiz-section">
      <div v-if="isLoadingQuiz" class="loading-state">
        <el-icon class="spin"><Loading /></el-icon>
        <div class="progress-text">{{ quizLoadingMsgs[quizLoadingIdx] }}</div>
        <div class="progress-time">已用时 {{ quizLoadingTime }} 秒</div>
        <div class="stream-box" v-if="quizStreamText">
          <pre><code>{{ quizStreamText }}</code></pre>
        </div>
      </div>
      <div v-else-if="quizQuestions.length">
        <div class="quiz-header">
          <h3>📝 小测验 — {{ itemTitle }}</h3>
          <span class="attempt-badge">第 {{ attemptNumber }} 次</span>
        </div>

        <div v-for="(q, i) in quizQuestions" :key="q.id" class="question-card">
          <div class="q-num">第 {{ i + 1 }} 题</div>
          <div class="q-text" v-html="renderMd(q.question)" />

          <!-- 选择题 -->
          <div v-if="q.type === 'choice'" class="choice-options">
            <div v-for="opt in q.options" :key="opt"
              class="option" :class="{selected: quizAnswers[i] === opt[0]}"
              @click="quizAnswers[i] = opt[0]">
              <span v-html="renderMd(opt)" />
            </div>
          </div>

          <!-- 简答题（支持图片）-->
          <div v-else class="open-answer">
            <el-input v-model="quizAnswers[i]" type="textarea" :rows="3"
              placeholder="请回答，或上传手写图片..." />
            <label class="photo-btn">
              📷 上传手写
              <input type="file" accept="image/*" @change="e => handleQuizPhoto(e, i)" hidden />
            </label>
            <img v-if="quizPhotoUrls[i]" :src="quizPhotoUrls[i]" class="photo-preview" />
          </div>
        </div>

        <el-button type="primary" size="large" class="submit-quiz-btn"
          :loading="isSubmittingQuiz" @click="submitQuiz"
          :disabled="quizAnswers.some(a => !a)">
          提交答案
        </el-button>
      </div>
    </div>

    <!-- 测验结果 -->
    <div v-if="phase === 'result'" class="result-section">
      <div class="result-card" :class="quizPassed ? 'passed' : 'failed'">
        <div class="result-icon">{{ quizPassed ? '🎉' : '😅' }}</div>
        <h3>{{ quizPassed ? '通过！' : '还需努力' }}</h3>
        <div class="score-circle">{{ quizScore }}分</div>
        <div class="feedback-content" v-html="renderMd(quizFeedback)" />

        <div class="result-actions">
          <template v-if="quizPassed">
            <el-button type="success" size="large" @click="$router.back()">
              返回大纲，继续学习 →
            </el-button>
          </template>
          <template v-else>
            <el-button size="large" @click="reteach">重新上课</el-button>
            <el-button type="primary" size="large" @click="retryQuiz">换题再考</el-button>
          </template>
        </div>
      </div>
    </div>

    <!-- 测验历史抽屉 -->
    <el-drawer v-model="showHistory" title="🕰️ 历史测验记录" size="400px" class="history-drawer">
      <div v-if="loadingHistory" class="history-loading">
        <el-icon class="spin"><Loading /></el-icon> 正在加载记录...
      </div>
      <div v-else-if="!quizHistoryList.length" class="history-empty">
        暂无测验记录
      </div>
      <div v-else class="history-list">
        <div v-for="q in quizHistoryList" :key="q.id" class="history-card" :class="[q.passed ? 'passed' : 'failed', q.type]">
          <div class="hc-header">
            <span class="hc-title">
              <el-tag v-if="q.type === 'assessment'" size="small" effect="dark" type="warning" class="mr-1">诊断</el-tag>
              {{ q.item_title }}
            </span>
            <span class="hc-date">{{ formatDate(q.created_at) }}</span>
          </div>
          <div class="hc-meta">
            <el-tag size="small" :type="q.passed ? 'success' : 'danger'">{{ q.passed ? '通过' : '未通过' }}</el-tag>
            <span class="hc-score">{{ q.score }} 分 {{ q.type === 'quiz' ? `(第 ${q.attempt_number} 次尝试)` : '' }}</span>
          </div>
          
          <el-collapse class="hc-details">
            <el-collapse-item title="查看题目与解析" :name="q.id">
              <div class="analysis-box">
                <div v-for="(question, idx) in q.questions" :key="idx" class="analysis-item">
                  <div class="ai-q">问：{{ question.question || question }}</div>
                  <div class="ai-a">答：{{ q.answers[idx] }}</div>
                </div>
                <div class="ai-total-feedback">
                  <strong>老师总评：</strong>
                  <div v-html="renderMd(q.ai_feedback || '未生成评价')" />
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-drawer>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSession, startLesson, askQuestion as apiAsk, startQuiz as apiStartQuiz, submitQuiz as apiSubmitQuiz, getSessionQuizzes } from '@/api/learning'
import { ArrowLeft, Loading, Delete, Clock } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const sessionId = Number(route.params.sessionId)
const itemDbId = Number(route.params.itemId)

const phase = ref<'lesson' | 'quiz' | 'result'>('lesson')
const phaseLabel: Record<string, string> = { lesson: '上课中', quiz: '小测验', result: '测验结果' }
const phaseTag: Record<string, string> = { lesson: 'primary', quiz: 'warning', result: '' }

const sessionSubject = ref('')
const itemTitle = ref('')
const conversationId = ref(0)
const lessonContent = ref('')
const question = ref('')
const qaHistory = ref<any[]>([])

// 动态加载状态（备课）
const lessonLoadingMsgs = ['👩‍🏫 正在准备教案...', '📖 补充生活中的通俗例子...', '⚠️ 总结易错点与注意事项...', '✨ 整理Markdown排版...']
const lessonLoadingIdx = ref(0)
const lessonLoadingTime = ref(0)
let lessonTimer: any = null

const isLoading = ref(false)
const isAsking = ref(false)
const isStartingQuiz = ref(false)

// 动态加载状态（出题）
const quizLoadingMsgs = ['📝 分析知识点掌握要求...', '🤔 构思变形测试题...', '✍️ 编写主观与客观题...', '⚖️ 校验题目难度与科学性...']
const quizLoadingIdx = ref(0)
const quizLoadingTime = ref(0)
let quizTimer: any = null

const isLoadingQuiz = ref(false)
const isSubmittingQuiz = ref(false)
const quizId = ref(0)
const quizQuestions = ref<any[]>([])
const quizAnswers = ref<string[]>([])
const quizPhotoFiles = ref<(File | null)[]>([])
const quizPhotoUrls = ref<string[]>([])
const quizScore = ref(0)
const quizPassed = ref(false)
const quizFeedback = ref('')
const attemptNumber = ref(1)

import { renderMd } from '@/utils/markdown'

const renderedContent = ref('')

// 将扁平的问答历史数组按对部分起来
// [{role:'user',...}, {role:'assistant',...}, ...] -> [{question, answer}, ...]
const qaPairs = computed(() => {
  const pairs = []
  const hist = qaHistory.value
  for (let i = 0; i < hist.length - 1; i += 2) {
    if (hist[i].role === 'user' && hist[i + 1]?.role === 'assistant') {
      pairs.push({ question: hist[i].content, answer: hist[i + 1].content })
    }
  }
  return pairs
})

// 删除一对问答（同时删除 user 问和 assistant 答）
function deleteQaPair(pairIdx: number) {
  const startIdx = pairIdx * 2
  if (startIdx >= 0 && startIdx + 1 < qaHistory.value.length) {
    qaHistory.value.splice(startIdx, 2)
  }
}

onMounted(async () => {
  isLoading.value = true
  lessonLoadingIdx.value = 0
  lessonLoadingTime.value = 0
  lessonTimer = setInterval(() => {
    lessonLoadingTime.value++
    if (lessonLoadingTime.value % 3 === 0 && lessonLoadingIdx.value < lessonLoadingMsgs.length - 1) {
      lessonLoadingIdx.value++
    }
  }, 1000)

  try {
    const s: any = await getSession(sessionId)
    sessionSubject.value = s.subject
    const res: any = await startLesson(sessionId, itemDbId, false)
    conversationId.value = res.conversation_id
    lessonContent.value = res.lesson_content
    itemTitle.value = res.item_title
    renderedContent.value = renderMd(res.lesson_content)
    qaHistory.value = res.history || []
    attemptNumber.value = res.attempt || 1
  } catch (e: any) {
    console.error(e)
  } finally { 
    isLoading.value = false
    clearInterval(lessonTimer)
  }
})

async function askQuestion() {
  if (!question.value.trim()) return
  isAsking.value = true
  const q = question.value
  question.value = ''
  qaHistory.value.push({ role: 'user', content: q })
  qaHistory.value.push({ role: 'assistant', content: '💬 老师正在思考...' })
  try {
    const res: any = await apiAsk(sessionId, conversationId.value, q)
    qaHistory.value[qaHistory.value.length - 1].content = res.answer
  } catch {
    qaHistory.value[qaHistory.value.length - 1].content = '网络错误，请重试。'
  } finally { isAsking.value = false }
}

const quizStreamText = ref('')

async function startQuiz() {
  isStartingQuiz.value = true
  isLoadingQuiz.value = true
  phase.value = 'quiz'
  quizStreamText.value = ''
  
  quizLoadingIdx.value = 0
  quizLoadingTime.value = 0
  quizTimer = setInterval(() => {
    quizLoadingTime.value++
    if (quizLoadingTime.value % 3 === 0 && quizLoadingIdx.value < quizLoadingMsgs.length - 1) {
      quizLoadingIdx.value++
    }
  }, 1000)

  try {
    const res: any = await startQuizStream(sessionId, conversationId.value, itemDbId, (chunk) => {
      quizStreamText.value += chunk
    })
    if (res && res.quiz_id) {
      quizId.value = res.quiz_id
      quizQuestions.value = res.questions || []
      quizAnswers.value = new Array(quizQuestions.value.length).fill('')
      quizPhotoFiles.value = new Array(quizQuestions.value.length).fill(null)
      quizPhotoUrls.value = new Array(quizQuestions.value.length).fill('')
      attemptNumber.value = res.attempt_number
    } else {
      // 流式请求返回 null（未收到 done 事件），回退到普通 API
      console.warn('流式出题空，回退到普通接口...')
      const r: any = await apiStartQuiz(sessionId, conversationId.value, itemDbId)
      quizId.value = r.quiz_id
      quizQuestions.value = r.questions || []
      quizAnswers.value = new Array(quizQuestions.value.length).fill('')
      quizPhotoFiles.value = new Array(quizQuestions.value.length).fill(null)
      quizPhotoUrls.value = new Array(quizQuestions.value.length).fill('')
      attemptNumber.value = r.attempt_number
    }
  } catch (e) {
    console.error('小测验加载失败:', e)
    // 流式和普通接口都失败，尝试一次普通接口作为最后保障
    try {
      const r: any = await apiStartQuiz(sessionId, conversationId.value, itemDbId)
      quizId.value = r.quiz_id
      quizQuestions.value = r.questions || []
      quizAnswers.value = new Array(quizQuestions.value.length).fill('')
      quizPhotoFiles.value = new Array(quizQuestions.value.length).fill(null)
      quizPhotoUrls.value = new Array(quizQuestions.value.length).fill('')
      attemptNumber.value = r.attempt_number
    } catch (e2) {
      console.error('备用接口也失败:', e2)
    }
  } finally { 
    isStartingQuiz.value = false
    isLoadingQuiz.value = false
    clearInterval(quizTimer)
  }
}

function handleQuizPhoto(e: Event, idx: number) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  quizPhotoFiles.value[idx] = file
  quizPhotoUrls.value[idx] = URL.createObjectURL(file)
  if (!quizAnswers.value[idx]) quizAnswers.value[idx] = '[图片答案]'
}

async function submitQuiz() {
  isSubmittingQuiz.value = true
  try {
    const images = quizPhotoFiles.value.filter(Boolean) as File[]
    const res: any = await apiSubmitQuiz(sessionId, quizId.value, itemDbId, quizAnswers.value, images)
    quizScore.value = res.score
    quizPassed.value = res.passed
    quizFeedback.value = res.feedback
    phase.value = 'result'
  } catch {} finally { isSubmittingQuiz.value = false }
}

function reteach() {
  // 直接恢复到已有课堂内容，无需重新生成教案
  qaHistory.value = []
  phase.value = 'lesson'
}

async function retryQuiz() {
  quizQuestions.value = []
  phase.value = 'quiz'
  await startQuiz()
}
// ── 测验历史功能 ──
const showHistory = ref(false)
const loadingHistory = ref(false)
const quizHistoryList = ref<any[]>([])

const formatDate = (ds: string) => {
  if (!ds) return ''
  const d = new Date(ds)
  return `${d.getMonth()+1}-${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

async function openHistory() {
  showHistory.value = true
  loadingHistory.value = true
  try {
    const res: any = await getSessionQuizzes(sessionId)
    quizHistoryList.value = res.quizzes || []
  } catch (e) {
    console.error(e)
  } finally {
    loadingHistory.value = false
  }
}

</script>

<style scoped lang="scss">
.classroom { width: 100%; display: flex; flex-direction: column; gap: 16px; }

.classroom-header {
  display: flex; justify-content: space-between; align-items: center;
  .header-center { display: flex; flex-direction: column; align-items: center; }
  .subject-badge { font-size: 11px; color: var(--color-text-secondary); }
  .item-title { font-size: 15px; font-weight: 700; }
  .header-right { display: flex; align-items: center; }
  .mr-2 { margin-right: 8px; }
}

.loading-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 60px; gap: 12px; background: #f8fafc; border-radius: 16px;
  .el-icon { font-size: 40px; color: #8b5cf6; }
  .progress-text { font-size: 16px; font-weight: 600; color: #1e293b; transition: all 0.3s; }
  .progress-time { font-size: 13px; color: #64748b; }
  .stream-box { 
    width: 100%; max-height: 200px; overflow-y: auto; text-align: left;
    background: #1e293b; color: #10b981; padding: 12px; border-radius: 8px;
    font-family: monospace; font-size: 13px; line-height: 1.4;
    white-space: pre-wrap; word-wrap: break-word;
    margin-top: 12px;
    pre { margin: 0; }
  }
}
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.lesson-card {
  background: white; border-radius: 16px; padding: 28px;
  box-shadow: 0 2px 12px rgba(0,0,0,.06);
}

.lesson-content {
  line-height: 1.9; font-size: 15px; margin-bottom: 24px;
  color: #1e293b;

  :deep(h2) {
    font-size: 18px; font-weight: 700; color: #1d4ed8;
    margin: 24px 0 10px; padding-bottom: 6px;
    border-bottom: 2px solid #e0e7ff;
  }
  :deep(h3) { font-size: 16px; font-weight: 600; color: #2563eb; margin: 16px 0 8px; }
  :deep(h4) { font-size: 15px; font-weight: 600; color: #374151; margin: 12px 0 6px; }

  :deep(p) { margin: 8px 0; }

  :deep(ul), :deep(ol) {
    padding-left: 1.6em;
    margin: 8px 0;
    :deep(li) { margin: 4px 0; }
  }

  :deep(code) { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #d63384; }
  :deep(pre) { background: #1e293b; color: #e2e8f0; padding: 14px 18px; border-radius: 10px; margin: 12px 0; overflow-x: auto; }
  :deep(strong) { color: #1e40af; }
  :deep(hr) { border: none; border-top: 1px solid #e2e8f0; margin: 16px 0; }

  :deep(blockquote) {
    border-left: 4px solid #8b5cf6; background: #f5f3ff;
    padding: 10px 16px; border-radius: 0 8px 8px 0; margin: 12px 0;
    color: #4c1d95;
  }

  /* KaTeX 运算公式的格式修正 */
  :deep(.katex-display) {
    margin: 1em 0;
    text-align: center;
    overflow-x: auto;
    padding: 4px 0;
  }
  :deep(.katex) {
    font-size: 1.05em;
  }
}

.qa-section { border-top: 1px solid var(--color-border-lighter); padding-top: 16px; }
.qa-history { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; max-height: 280px; overflow-y: auto; }
.qa-msg {
  display: flex; gap: 8px;
  &.user { flex-direction: row-reverse; .role-badge { background: #8b5cf6; } }
  &.assistant { .role-badge { background: #10b981; } }
  .role-badge { flex-shrink: 0; height: 24px; padding: 0 8px; border-radius: 12px; font-size: 11px; color: white; display: flex; align-items: center; }
  .msg-content { background: #f8fafc; border-radius: 10px; padding: 10px 14px; font-size: 14px; max-width: 80%; }
}

.qa-input-row { display: flex; gap: 10px; }
.ready-row { display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--color-border-lighter); }
.ready-tip { font-size: 13px; color: var(--color-text-secondary); margin: 0; }

.quiz-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; h3 { margin: 0; } }
.attempt-badge { background: #fef3c7; color: #d97706; padding: 4px 10px; border-radius: 20px; font-size: 12px; }

.question-card {
  background: white; border-radius: 14px; padding: 22px;
  margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.05);
  .q-num { font-size: 12px; color: var(--color-text-secondary); margin-bottom: 6px; }
  .q-text { font-size: 16px; font-weight: 600; margin-bottom: 14px; line-height: 1.5; }
}

.choice-options { display: flex; flex-direction: column; gap: 8px; }
.option {
  padding: 12px 16px; border-radius: 8px; border: 2px solid var(--color-border-lighter);
  cursor: pointer; transition: all .15s;
  &:hover { border-color: #8b5cf6; background: #f5f3ff; }
  &.selected { border-color: #8b5cf6; background: #ede9fe; font-weight: 600; }
}

.open-answer { display: flex; flex-direction: column; gap: 8px; }
.photo-btn {
  display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px;
  border-radius: 8px; border: 1px dashed #8b5cf6; color: #8b5cf6;
  cursor: pointer; font-size: 13px; width: fit-content;
}
.photo-preview { width: 80px; height: 60px; object-fit: cover; border-radius: 8px; }

.submit-quiz-btn { width: 100%; height: 48px; font-size: 15px; margin-top: 8px; border-radius: 12px; }

.result-section { display: flex; justify-content: center; }
.result-card {
  background: white; border-radius: 20px; padding: 40px; text-align: center;
  box-shadow: 0 4px 24px rgba(0,0,0,.08); max-width: 540px; width: 100%;
  border: 3px solid transparent;
  &.passed { border-color: #86efac; }
  &.failed { border-color: #fca5a5; }
  .result-icon { font-size: 52px; margin-bottom: 12px; }
  h3 { font-size: 22px; font-weight: 800; margin: 0 0 16px; }
}

.score-circle {
  width: 90px; height: 90px; border-radius: 50%; margin: 0 auto 20px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white; font-size: 26px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
}

.feedback-content { text-align: left; background: #f8fafc; border-radius: 12px; padding: 16px; margin-bottom: 24px; font-size: 14px; line-height: 1.8; }
.result-actions { display: flex; gap: 12px; justify-content: center; }

.qa-pair {
  position: relative;
  padding: 6px 0;
  border-bottom: 1px dashed var(--color-border-lighter);
  &:last-child { border-bottom: none; }
  &:hover .qa-delete-btn { opacity: 1; }
}

.qa-delete-btn {
  position: absolute;
  top: 8px;
  right: 0;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s, color 0.2s;
  color: #94a3b8;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  &:hover { color: #ef4444; background: #fee2e2; }
  .el-icon { font-size: 15px; }
}

/* 测验历史样式 */
.history-drawer {
  .history-loading { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 40px; color: #64748b; }
  .history-empty { text-align: center; padding: 40px; color: #94a3b8; }
  .history-list { display: flex; flex-direction: column; gap: 16px; padding: 0 16px 20px; }
  .history-card {
    background: #f8fafc; border-radius: 12px; padding: 16px; border-left: 4px solid #cbd5e1;
    &.passed { border-left-color: #10b981; }
    &.failed { border-left-color: #ef4444; }
    &.assessment { border-left-color: #f59e0b; background: #fffcf0; }
  }
  .hc-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .hc-title { font-weight: 700; font-size: 15px; color: #1e293b; display: flex; align-items: center; }
  .hc-date { font-size: 12px; color: #94a3b8; }
  .hc-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
  .hc-score { font-size: 13px; font-weight: 600; color: #334155; }
  .mr-1 { margin-right: 4px; }
  
  .hc-details {
    border: none;
    :deep(.el-collapse-item__header) {
      height: 32px; line-height: 32px; background: transparent; border: none; font-size: 12px; color: #6366f1;
    }
    :deep(.el-collapse-item__wrap) { background: transparent; border: none; }
    :deep(.el-collapse-item__content) { padding-bottom: 0; }
  }

  .analysis-box {
    font-size: 13px; color: #475569;
    .analysis-item {
      padding: 8px; background: white; border-radius: 6px; margin-bottom: 8px; border: 1px solid #f1f5f9;
      .ai-q { font-weight: 600; color: #1e293b; margin-bottom: 4px; }
      .ai-a { color: #64748b; font-style: italic; }
    }
    .ai-total-feedback {
      margin-top: 12px; padding: 12px; background: #f1f5f9; border-radius: 8px;
      strong { display: block; margin-bottom: 6px; color: #1e293b; }
      :deep(p) { margin: 4px 0; }
    }
  }
}
</style>
