<template>
  <div class="assessment">
    <!-- 初始加载中 -->
    <div v-if="isInitialLoading" class="initial-loading">
      <el-icon class="spin" style="font-size:48px;color:#8b5cf6"><Loading /></el-icon>
      <p>正在加载测评进度...</p>
    </div>

    <!-- 开始前 -->
    <div v-else-if="phase === 'intro'" class="intro-card">
      <div class="intro-icon">🎯</div>
      <h2>入学评测</h2>
      <p>AI 将出 10 道诊断题，评估你在「{{ subject }}」各领域的基础，生成个性化学习大纲</p>
      <ul class="tips">
        <li>📝 题型：选择题 + 简答题</li>
        <li>⏱️ 预计 10-15 分钟</li>
        <li>🎯 目的是帮 AI 了解你，没有"不及格"</li>
        <li>📸 简答题支持文字或拍照作答</li>
      </ul>
      <div class="assessment-settings" v-if="!isGenerating && hasPreviousProgress">
        <el-button type="info" plain size="small" @click="startAssessment(true)">
          ♻️ 换一批题目
        </el-button>
      </div>

      <el-button type="primary" size="large" @click="startAssessment(false)" class="start-btn" :loading="isGenerating" :disabled="isGenerating">
        {{ isGenerating ? '正在为你生成测评题目...' : (hasPreviousProgress ? '继续评测' : '开始评测') }}
      </el-button>
      
      <div v-if="isGenerating" class="generating-progress">
        <el-icon class="spin"><Loading /></el-icon>
        <div class="progress-text">{{ loadingMessages[loadingIndex] }}</div>
        <div class="progress-time">已用时 {{ loadingTime }} 秒</div>
        <div v-if="streamText" class="stream-box">
          <pre>{{ streamText }}</pre>
        </div>
      </div>
    </div>

    <!-- 答题中 -->
    <div v-else-if="phase === 'answering'" class="answering">
      <div class="progress-header">
        <div class="progress-info">
          <span class="subject-tag">{{ subject }}</span>
          <span>第 {{ currentIdx + 1 }} / {{ questions.length }} 题</span>
        </div>
        <el-progress :percentage="((currentIdx) / questions.length * 100)" :stroke-width="6" style="width:200px" />
      </div>

      <div class="question-card">
        <div class="q-meta">
          <el-tag size="small" :type="diffTag(currentQ.difficulty)">{{ currentQ.difficulty }}</el-tag>
          <el-tag size="small" plain>{{ currentQ.domain }}</el-tag>
        </div>
        <div class="q-text">
          <ContentRenderer :content="(currentIdx + 1) + '. ' + currentQ.question" />
        </div>

        <!-- 选择题 -->
        <div v-if="currentQ.type === 'choice'" class="choice-options">
          <div v-for="opt in currentQ.options" :key="opt"
            class="option" :class="{selected: answers[currentIdx] === opt[0]}"
            @click="answers[currentIdx] = opt[0]; autoSave()">
            <div class="option-content">
              <ContentRenderer :content="opt" />
            </div>
          </div>
        </div>

        <!-- 简答题 -->
        <div v-else class="open-answer">
          <el-input v-model="answers[currentIdx]" type="textarea" :rows="4"
            placeholder="请输入你的答案，或点击📷上传手写照片" @blur="autoSave" />
          <div class="photo-upload">
            <label class="photo-btn">
              📷 上传手写
              <input type="file" accept="image/*" @change="e => handlePhoto(e, currentIdx)" hidden />
            </label>
            <img v-if="photoUrls[currentIdx]" :src="photoUrls[currentIdx]"
              class="photo-preview" alt="答题图片" />
          </div>
        </div>

        <div class="nav-row">
          <el-button @click="currentIdx = Math.max(0, currentIdx - 1)"
            :disabled="currentIdx === 0">← 上一题</el-button>
          <span class="dot-nav">
            <span v-for="(_, i) in questions" :key="i"
              class="dot" :class="{active: i === currentIdx, answered: answers[i]}"
              @click="currentIdx = i" />
          </span>
          <el-button v-if="currentIdx < questions.length - 1" type="primary"
            @click="currentIdx++; autoSave()" :disabled="!answers[currentIdx]">下一题 →</el-button>
          <el-button v-else type="success" :loading="isSubmitting"
            @click="submitAssessment" :disabled="!allAnswered">提交评测</el-button>
        </div>
      </div>
    </div>

    <!-- 正在批改 -->
    <div v-else-if="phase === 'evaluating'" class="evaluating-state">
      <el-icon class="spin" style="font-size:48px;color:#8b5cf6"><Loading /></el-icon>
      <h3>AI 正在分析你的答题情况...</h3>
      <p>约 15-30 秒，请稍候</p>
    </div>

    <!-- 评测结果 -->
    <div v-else-if="phase === 'result'" class="result-card">
      <div class="result-header">
        <div class="result-icon">🎉</div>
        <h2>评测完成！</h2>
        <p class="result-sub">AI 已分析你的基础，以下是评估报告</p>
      </div>

      <!-- 各领域熟练度 -->
      <div class="result-brief">
        <div class="score-box">
          <div class="score-circle">
            <span class="score-num">{{ overallScore }}</span>
            <span class="score-unit">综合评分</span>
          </div>
        </div>
        <div class="result-meta">
          <div class="meta-item">
            <span class="label">测评题目</span>
            <span class="val">{{ questions.length }} 道</span>
          </div>
          <div class="meta-item">
            <span class="label">核心考点</span>
            <span class="val">{{ Object.keys(proficiency).filter(k => k !== '__overall__').length }} 个</span>
          </div>
        </div>
      </div>

      <!-- AI 评语 -->
      <div class="report-section">
        <h3>📋 AI 报告摘要</h3>
        <div class="report-content">
          <ContentRenderer :content="assessmentReport" />
        </div>
      </div>

      <!-- 题目回顾 -->
      <div v-if="questionResults && questionResults.length > 0" class="review-section">
        <h3>🔍 题目对错详情</h3>
        <div class="review-list">
          <div v-for="(res, idx) in questionResults" :key="idx" class="review-item"
            :class="res.is_correct ? 'correct' : 'incorrect'">
            <div class="review-q-header">
              <span class="res-idx">#{{ idx + 1 }}</span>
              <span class="res-status-tag" :class="res.is_correct ? 'pass' : 'fail'">
                {{ res.is_correct ? '正确' : '待提升' }}
              </span>
              <span class="res-score">{{ res.score }}分</span>
            </div>
            <div class="res-q-text"><strong>问：</strong>{{ questions[idx]?.question || '题目已失效' }}</div>
            <div class="res-a-text"><strong>你的答案：</strong>{{ answers[idx] }}</div>
            <div v-if="res.feedback" class="res-feedback">📝 点评：{{ res.feedback }}</div>
            <div v-if="res.explanation" class="res-explanation">💡 解析：{{ res.explanation }}</div>
          </div>
        </div>
      </div>

      <!-- 各领域熟练度 -->
      <div class="proficiency-section" v-if="filteredProficiencyCount">
        <h3>📊 各领域掌握程度</h3>
        <div class="proficiency-list">
          <template v-for="(score, domain) in proficiency" :key="domain">
            <div v-if="domain !== '__overall__'" class="prof-item">
              <div class="prof-label">
                <span class="domain-name">{{ domain }}</span>
                <span class="domain-score">{{ score }}分</span>
              </div>
              <el-progress
                :percentage="score"
                :color="score >= 70 ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444'"
                :stroke-width="10"
                :show-text="false"
              />
            </div>
          </template>
        </div>
      </div>

      <el-button type="primary" size="large" class="goto-syllabus-btn" @click="goToSyllabus">
        进入个性化学习大纲 →
      </el-button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSession, startAssessmentStream, startAssessment as apiStart, submitAssessment as apiSubmit, saveAssessmentAnswers } from '@/api/learning'
import { Loading } from '@element-plus/icons-vue'
import ContentRenderer from '@/components/ContentRenderer.vue'

const route = useRoute()
const router = useRouter()
const sessionId = Number(route.params.sessionId)
const subject = ref('')
const phase = ref<'intro' | 'answering' | 'evaluating' | 'result'>('intro')
const isGenerating = ref(false)
const isSubmitting = ref(false)
const assessmentReport = ref('')
const proficiency = ref<Record<string, number>>({})
const overallScore = ref(0)
const questionResults = ref<any[]>([])
const hasPreviousProgress = ref(false)
const isInitialLoading = ref(true)

const filteredProficiencyCount = computed(() => 
  Object.keys(proficiency.value).filter(k => k !== '__overall__').length
)

// 动态加载状态
const loadingMessages = ['🚀 初始化 AI 评估引擎...', '🧠 分析学科知识图谱...', '📝 自动生成诊断选择题...', '✍️ 自动生成深度简答题...', '⚖️ 校验题目难度与逻辑...']
const loadingIndex = ref(0)
const loadingTime = ref(0)
let timer: any = null
const streamText = ref('')
const openCount = ref(3) // 默认 3 道简答，包含 1 中 1 难

const questions = ref<any[]>([])
const answers = ref<string[]>([])
const photoFiles = ref<(File | null)[]>([])
const photoUrls = ref<string[]>([])
const currentIdx = ref(0)

const currentQ = computed(() => questions.value[currentIdx.value] || {})
const allAnswered = computed(() => answers.value.every(a => a && a.trim()))

const diffTag = (d: string): "success" | "warning" | "danger" | "info" => {
  const map: Record<string, "success" | "warning" | "danger" | "info"> = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return map[d] || 'info'
}

onMounted(async () => {
  window.addEventListener('visibilitychange', handleVisibilityChange)
  try {
    const s: any = await getSession(sessionId)
    subject.value = s.subject
    
    // 1. 如果已经有大纲条目，说明测评彻底完成并生成了大纲，跳到大纲页
    if (s.syllabus_items?.length > 0) {
      router.replace(`/session/${sessionId}/syllabus`)
      return
    }

    // 2. 检查测评记录
    if (s.assessment) {
      // 如果已完成测评（但可能还没生成大纲或还在结果页刷新的）
      if (s.assessment.completed) {
        // 加载已保存的结果
        questions.value = s.assessment.questions || []
        answers.value = s.assessment.answers || []
        proficiency.value = s.assessment.proficiency_result || {}
        overallScore.value = proficiency.value['__overall__'] || 0
        assessmentReport.value = s.assessment.ai_report || ''
        questionResults.value = s.assessment.question_results || []
        phase.value = 'result'
        return
      }

      // 如果未完成但有题目，自动进入答题状态或生成状态
      if (s.assessment.has_questions || s.assessment.id) {
        hasPreviousProgress.value = true
        // 自动触发开始逻辑以恢复进度
        await startAssessment()
        
        // 【优化】智能恢复题号：定位到第一个未答题
        if (questions.value.length > 0) {
          const firstEmpty = answers.value.findIndex(a => !a || !a.trim())
          if (firstEmpty !== -1) {
            currentIdx.value = firstEmpty
          } else {
            // 如果都答了但没提交，定位到最后一题
            currentIdx.value = questions.value.length - 1
          }
        }
      }
    }
  } catch (e) {
    console.error('Mount check failed:', e)
  } finally {
    isInitialLoading.value = false
  }
})

import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('visibilitychange', handleVisibilityChange)
  autoSave() // 离开页面前尝试保存一次
})

function handleVisibilityChange() {
  if (document.visibilityState === 'hidden') {
    autoSave()
  }
}

async function startAssessment(forceNew = false) {
  isGenerating.value = true
  streamText.value = ''
  
  if (forceNew) {
    questions.value = []
    answers.value = []
  }
  
  // 启动动态提示定时器
  loadingIndex.value = 0
  loadingTime.value = 0
  timer = setInterval(() => {
    loadingTime.value++
    if (loadingTime.value % 3 === 0 && loadingIndex.value < loadingMessages.length - 1) {
      loadingIndex.value++
    }
  }, 1000)

  try {
    // 先尝试流式 API
    const res: any = await startAssessmentStream(sessionId, (chunk) => {
      streamText.value += chunk
    }, openCount.value, forceNew)
    if (res && res.questions && res.questions.length > 0) {
      questions.value = res.questions
      // 这里的 answers 如果后端返回了（断点续传），就用原来的；没有就新建空数组
      const restoredAnswers = res.answers || []
      answers.value = new Array(questions.value.length).fill('')
      restoredAnswers.forEach((val: string, idx: number) => {
        if (idx < answers.value.length) answers.value[idx] = val
      })
      
      photoUrls.value = new Array(questions.value.length).fill('')
      
      if (res.completed) {
        proficiency.value = res.proficiency_result || {}
        overallScore.value = proficiency.value['__overall__'] || 0
        assessmentReport.value = res.ai_report || ''
        questionResults.value = res.question_results || []
        phase.value = 'result'
      } else {
        phase.value = 'answering'
      }
      return
    }
    // 流式返回 null 或空，回退到普通 API
    console.warn('流式评测失败，回退到普通接口...')
  } catch (e: any) {
    console.warn('流式评测出错，回退到普通接口:', e)
  }

  // 回退：使用普通 API
  try {
    const r: any = await apiStart(sessionId, openCount.value, forceNew)
    questions.value = r.questions || []
    
    const restoredAnswers = r.answers || []
    answers.value = new Array(questions.value.length).fill('')
    restoredAnswers.forEach((val: string, idx: number) => {
      if (idx < answers.value.length) answers.value[idx] = val
    })

    photoFiles.value = new Array(questions.value.length).fill(null)
    photoUrls.value = new Array(questions.value.length).fill('')
    
    if (r.completed) {
      proficiency.value = r.proficiency_result || {}
      overallScore.value = proficiency.value['__overall__'] || 0
      assessmentReport.value = r.ai_report || ''
      questionResults.value = r.question_results || []
      phase.value = 'result'
    } else {
      phase.value = 'answering'
    }
  } catch (e2: any) {
    console.error('评测加载失败:', e2)
  } finally { 
    isGenerating.value = false
    clearInterval(timer)
  }
}

async function autoSave() {
  try {
    await saveAssessmentAnswers(sessionId, answers.value)
  } catch (e) {
    console.warn('Auto-save failed:', e)
  }
}

function handlePhoto(e: Event, idx: number) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  photoFiles.value[idx] = file
  photoUrls.value[idx] = URL.createObjectURL(file)
  if (!answers.value[idx]) answers.value[idx] = '[图片答案]'
  autoSave()
}

async function submitAssessment() {
  isSubmitting.value = true
  phase.value = 'evaluating'
  try {
    const result: any = await apiSubmit(sessionId, answers.value)
    // 保存评语和熟练度
    assessmentReport.value = result.report || ''
    proficiency.value = result.proficiency || {}
    overallScore.value = result.overall_score || proficiency.value['__overall__'] || 0
    questionResults.value = result.question_results || []
    // 生成大纲（后台）
    const { generateSyllabusForSession } = await import('@/api/learning')
    await generateSyllabusForSession(sessionId, subject.value)
    // 显示结果页
    phase.value = 'result'
  } catch (e: any) {
    console.error(e)
    phase.value = 'answering'
    isSubmitting.value = false
  }
}

function goToSyllabus() {
  router.push(`/session/${sessionId}/syllabus`)
}
</script>

<style scoped lang="scss">
.assessment { width: 100%; }

.intro-card {
  background: white; border-radius: 20px; padding: 48px;
  text-align: center; box-shadow: 0 4px 24px rgba(0,0,0,.08);
  .intro-icon { font-size: 56px; margin-bottom: 16px; }
  h2 { font-size: 24px; font-weight: 800; margin: 0 0 12px; }
  p { color: var(--color-text-secondary); margin-bottom: 24px; }
  .tips { text-align: left; display: block; max-width: 340px; margin: 0 auto 32px; li { margin-bottom: 8px; } }
  .assessment-settings {
    margin-bottom: 24px;
    display: flex; justify-content: center;
  }
  .start-btn { height: 48px; padding: 0 40px; font-size: 16px; border-radius: 12px; background: linear-gradient(135deg, #8b5cf6, #6d28d9); border: none; }
}

.generating-progress {
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  margin-top: 20px; padding: 24px; background: #f8fafc; border-radius: 12px;
  .el-icon { font-size: 32px; color: #8b5cf6; }
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

.progress-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
  .progress-info { display: flex; align-items: center; gap: 12px; }
  .subject-tag { background: #ede9fe; color: #6d28d9; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }
}

.question-card {
  background: white; border-radius: 16px; padding: 32px;
  box-shadow: 0 2px 12px rgba(0,0,0,.06);
  .q-meta { display: flex; gap: 8px; margin-bottom: 16px; }
  .q-text { font-size: 17px; font-weight: 600; line-height: 1.6; margin-bottom: 24px; }
}

.choice-options { display: flex; flex-direction: column; gap: 10px; }
.option {
  padding: 14px 18px; border-radius: 10px; border: 2px solid var(--color-border-lighter);
  cursor: pointer; transition: all .15s; font-size: 15px;
  &:hover { border-color: #8b5cf6; background: #f5f3ff; }
  &.selected { border-color: #8b5cf6; background: #ede9fe; font-weight: 600; }
}

.open-answer { .el-input { margin-bottom: 10px; } }
.photo-upload { display: flex; align-items: center; gap: 12px; }
.photo-btn {
  display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px;
  border-radius: 8px; border: 1px dashed #8b5cf6; color: #8b5cf6;
  cursor: pointer; font-size: 13px; &:hover { background: #f5f3ff; }
}
.photo-preview { width: 80px; height: 60px; object-fit: cover; border-radius: 8px; border: 1px solid #ddd; }

.nav-row { display: flex; justify-content: space-between; align-items: center; margin-top: 28px; }
.dot-nav { display: flex; gap: 6px; }
.dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: #e5e7eb; cursor: pointer; transition: all .15s;
  &.active { background: #8b5cf6; transform: scale(1.3); }
  &.answered { background: #67c23a; }
}

.evaluating-state {
  display: flex; flex-direction: column; align-items: center; gap: 16px;
  padding: 80px; text-align: center;
  h3 { font-size: 20px; font-weight: 700; }
  p { color: var(--color-text-secondary); }
}
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 评测结果页 ── */
.result-card {
  background: white; border-radius: 20px; padding: 40px;
  box-shadow: 0 4px 24px rgba(0,0,0,.08);
  display: flex; flex-direction: column; gap: 28px;
}

.result-header {
  text-align: center;
  margin-bottom: -10px;
  .result-icon { font-size: 56px; margin-bottom: 12px; }
  h2 { font-size: 26px; font-weight: 800; margin: 0 0 8px; }
  .result-sub { color: var(--color-text-secondary); margin: 0; }
}

.result-brief {
  display: flex; align-items: center; justify-content: space-around;
  padding: 20px; background: #f1f5f9; border-radius: 16px;
  .score-box {
    .score-circle {
      width: 120px; height: 120px; border-radius: 50%;
      background: white; border: 8px solid #8b5cf6;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
      .score-num { font-size: 42px; font-weight: 900; color: #6d28d9; line-height: 1; }
      .score-unit { font-size: 12px; color: #64748b; margin-top: 4px; }
    }
  }
  .result-meta {
    display: flex; gap: 40px;
    .meta-item {
      display: flex; flex-direction: column; align-items: center;
      .label { font-size: 13px; color: #64748b; margin-bottom: 4px; }
      .val { font-size: 20px; font-weight: 700; color: #1e293b; }
    }
  }
}

.report-section {
  background: #f8fafc; border-radius: 14px; padding: 24px;
  h3 { font-size: 16px; font-weight: 700; color: #1e293b; margin: 0 0 14px; }
  .report-content {
    font-size: 15px; line-height: 1.8; color: #374151;
    :deep(p) { margin: 6px 0; }
    :deep(strong) { color: #1e40af; }
    :deep(ul), :deep(ol) { padding-left: 1.4em; margin: 8px 0; }
  }
}

.proficiency-section {
  h3 { font-size: 16px; font-weight: 700; color: #1e293b; margin: 0 0 16px; }
}

.proficiency-list { display: flex; flex-direction: column; gap: 12px; }

.prof-item {
  .prof-label {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 6px;
    .domain-name { font-size: 14px; font-weight: 500; color: #374151; }
    .domain-score { font-size: 14px; font-weight: 700; color: #6d28d9; }
  }
}

.goto-syllabus-btn {
  height: 52px; font-size: 16px; border-radius: 14px; align-self: center;
  padding: 0 48px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9); border: none;
}

.initial-loading {
  display: flex; flex-direction: column; align-items: center; gap: 16px;
  padding: 100px 0; color: #64748b; font-size: 16px;
}

/* 题目回顾样式 */
.review-section {
  margin-top: 10px;
  h3 { font-size: 16px; font-weight: 700; color: #1e293b; margin: 0 0 16px; }
}
.review-list { display: flex; flex-direction: column; gap: 16px; }
.review-item {
  padding: 20px; border-radius: 12px; border-left: 5px solid #ddd;
  background: #fdfdfd; box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  &.correct { border-left-color: #10b981; background: #f0fdf4; }
  &.incorrect { border-left-color: #ef4444; background: #fef2f2; }

  .review-q-header {
    display: flex; align-items: center; gap: 10px; margin-bottom: 12px;
    .res-idx { font-weight: 800; color: #64748b; }
    .res-status-tag {
      padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 700;
      &.pass { background: #dcfce7; color: #166534; }
      &.fail { background: #fee2e2; color: #991b1b; }
    }
    .res-score { font-size: 13px; color: #64748b; margin-left: auto; }
  }
  .res-q-text { font-size: 14px; color: #1e293b; margin-bottom: 8px; line-height: 1.5; }
  .res-a-text { font-size: 14px; color: #475569; margin-bottom: 12px; font-style: italic; }
  .res-feedback { font-size: 13px; color: #4338ca; background: #e0e7ff; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; }
  .res-explanation { font-size: 13px; color: #059669; background: #ecfdf5; padding: 8px 12px; border-radius: 8px; }
}
</style>
