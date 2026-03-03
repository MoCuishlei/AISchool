<template>
  <div class="exam-page">
    <div class="exam-header">
      <el-button link @click="$router.back()"><el-icon><ArrowLeft /></el-icon> 返回</el-button>
      <h2>{{ examType === 'midterm' ? '📑 期中考试' : '🎓 期末考试' }}</h2>
      <el-tag :type="examType === 'final' ? 'danger' : 'warning'" size="large">
        {{ subject }}
      </el-tag>
    </div>

    <!-- 开始前 -->
    <div v-if="phase === 'intro'" class="intro-card">
      <div class="intro-icon">{{ examType === 'midterm' ? '📑' : '🎓' }}</div>
      <h3>{{ examType === 'midterm' ? '期中考试' : '期末考试' }}</h3>
      <ul class="exam-info">
        <li>📝 题数：{{ examType === 'midterm' ? '15' : '20' }} 道</li>
        <li>⏱️ 建议时间：{{ examType === 'midterm' ? '30' : '45' }} 分钟</li>
        <li>📊 考察范围：{{ examType === 'midterm' ? '已学完的知识点' : '全部大纲内容' }}</li>
        <li>🤖 AI 即时批改，给出详细评语</li>
      </ul>
      <el-button v-if="!isGenerating" type="primary" size="large" @click="generateExam" class="start-btn">
        开始考试
      </el-button>
      <div v-else class="generating-progress">
        <el-icon class="spin"><Loading /></el-icon>
        <div class="progress-text">{{ loadingMessages[loadingIndex] }}</div>
        <div class="progress-time">已用时 {{ loadingTime }} 秒</div>
        <div class="stream-box" v-if="streamText">
          <pre><code>{{ streamText }}</code></pre>
        </div>
      </div>
    </div>

    <!-- 答题 -->
    <div v-if="phase === 'answering'" class="answering">
      <div class="exam-progress">
        <span>{{ subject }} {{ examType === 'midterm' ? '期中' : '期末' }}考试</span>
        <el-progress :percentage="(currentIdx / questions.length * 100)" :stroke-width="6" style="width:180px"/>
        <span>{{ currentIdx + 1 }}/{{ questions.length }}</span>
      </div>

      <div class="question-card">
        <div class="q-head">
          <el-tag size="small" :type="diffTag(questions[currentIdx]?.difficulty)">
            {{ questions[currentIdx]?.difficulty }}
          </el-tag>
          <el-tag size="small" plain>{{ questions[currentIdx]?.domain }}</el-tag>
          <span class="q-score">{{ questions[currentIdx]?.score_weight || 5 }}分</span>
        </div>
        <div class="q-text" v-html="renderMd((currentIdx + 1) + '. ' + questions[currentIdx]?.question)" />

        <div v-if="questions[currentIdx]?.type === 'choice'" class="choice-options">
          <div v-for="opt in questions[currentIdx].options" :key="opt"
            class="option" :class="{selected: answers[currentIdx] === opt[0]}"
            @click="answers[currentIdx] = opt[0]">{{ opt }}</div>
        </div>

        <div v-else class="open-answer">
          <el-input v-model="answers[currentIdx]" type="textarea" :rows="4"
            placeholder="请作答，可上传手写图片..." />
          <label class="photo-btn">
            📷 上传手写
            <input type="file" accept="image/*" @change="e => handlePhoto(e, currentIdx)" hidden />
          </label>
          <img v-if="photoUrls[currentIdx]" :src="photoUrls[currentIdx]" class="photo-preview" />
        </div>

        <div class="nav-row">
          <el-button @click="currentIdx = Math.max(0, currentIdx - 1)" :disabled="currentIdx === 0">← 上题</el-button>
          <div class="dot-nav">
            <span v-for="(_, i) in questions" :key="i"
              class="dot" :class="{active: i === currentIdx, answered: answers[i]}"
              @click="currentIdx = i" />
          </div>
          <template v-if="currentIdx < questions.length - 1">
            <el-button type="primary" @click="currentIdx++">下题 →</el-button>
          </template>
          <template v-else>
            <el-button type="success" :loading="isSubmitting" @click="submitExam">
              交卷
            </el-button>
          </template>
        </div>
      </div>
    </div>

    <!-- 批改中 -->
    <div v-if="phase === 'grading'" class="grading-state">
      <el-icon class="spin"><Loading /></el-icon>
      <h3>AI 正在批改试卷...</h3>
      <p>约 20-30 秒</p>
    </div>

    <!-- 成绩报告 -->
    <div v-if="phase === 'result'" class="result-card">
      <div class="score-display">
        <div class="score-circle">{{ examScore }}</div>
        <div class="score-info">
          <h3>{{ examType === 'midterm' ? '期中考试' : '期末考试' }}成绩</h3>
          <p>{{ subject }}</p>
        </div>
      </div>
      <div class="report-content" v-html="renderMd(examReport)" />
      <el-button type="primary" @click="$router.push(`/session/${sessionId}/syllabus`)">
        返回大纲
      </el-button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSession, generateExamStream, submitExam as apiSubmit } from '@/api/learning'
import { ArrowLeft, Loading } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const sessionId = Number(route.params.sessionId)
const examType = route.params.examType as string

const subject = ref('')
const phase = ref<'intro' | 'answering' | 'grading' | 'result'>('intro')
const isGenerating = ref(false)
const isSubmitting = ref(false)

// 动态加载状态
const loadingMessages = ['🚀 根据进度匹配考试范围...', '🧠 分析知识图谱...', '📝 自动生成变形选择题...', '✍️ 自动生成深度简答题...', '⚖️ 校验整套试卷难度...']
const loadingIndex = ref(0)
const loadingTime = ref(0)
let timer: any = null
const streamText = ref('')

const examId = ref(0)
const questions = ref<any[]>([])
const answers = ref<string[]>([])
const photoFiles = ref<(File | null)[]>([])
const photoUrls = ref<string[]>([])
const currentIdx = ref(0)
const examScore = ref(0)
const examReport = ref('')
const diffTag = (d: string) => ({ easy: 'success', medium: 'warning', hard: 'danger' }[d] || 'info')
import { renderMd } from '@/utils/markdown'

onMounted(async () => {
  const s: any = await getSession(sessionId)
  subject.value = s.subject
})

async function generateExam() {
  isGenerating.value = true
  streamText.value = ''
  
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
    const res: any = await generateExamStream(sessionId, examType as 'midterm' | 'final', (chunk) => {
      streamText.value += chunk
    })
    examId.value = res.exam_id
    questions.value = res.questions || []
    answers.value = new Array(questions.value.length).fill('')
    photoFiles.value = new Array(questions.value.length).fill(null)
    photoUrls.value = new Array(questions.value.length).fill('')
    phase.value = 'answering'
  } catch (e: any) {
    console.error(e)
  } finally { 
    isGenerating.value = false
    clearInterval(timer)
  }
}

function handlePhoto(e: Event, idx: number) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  photoFiles.value[idx] = file
  photoUrls.value[idx] = URL.createObjectURL(file)
  if (!answers.value[idx]) answers.value[idx] = '[图片答案]'
}

async function submitExam() {
  isSubmitting.value = true
  phase.value = 'grading'
  try {
    const images = photoFiles.value.filter(Boolean) as File[]
    const res: any = await apiSubmit(sessionId, examId.value, answers.value, images)
    examScore.value = res.score
    examReport.value = res.report
    phase.value = 'result'
  } catch { phase.value = 'answering' } finally { isSubmitting.value = false }
}
</script>

<style scoped lang="scss">
.exam-page { max-width: 760px; display: flex; flex-direction: column; gap: 20px; }
.exam-header { display: flex; align-items: center; gap: 16px; h2 { flex:1; font-size: 20px; font-weight: 800; margin: 0; } }

.intro-card {
  background: white; border-radius: 20px; padding: 48px; text-align: center;
  box-shadow: 0 4px 24px rgba(0,0,0,.08);
  .intro-icon { font-size: 56px; margin-bottom: 12px; }
  h3 { font-size: 22px; font-weight: 800; margin: 0 0 20px; }
  .exam-info { text-align: left; display: inline-block; margin-bottom: 32px; li { margin-bottom: 8px; } }
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

.exam-progress { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; font-size: 14px; }

.question-card {
  background: white; border-radius: 16px; padding: 28px;
  box-shadow: 0 2px 12px rgba(0,0,0,.06);
}

.q-head { display: flex; gap: 8px; align-items: center; margin-bottom: 12px; }
.q-score { margin-left: auto; font-size: 13px; color: #8b5cf6; font-weight: 700; }
.q-text { font-size: 17px; font-weight: 600; line-height: 1.6; margin-bottom: 20px; }

.choice-options { display: flex; flex-direction: column; gap: 10px; }
.option {
  padding: 12px 16px; border-radius: 10px; border: 2px solid var(--color-border-lighter);
  cursor: pointer; transition: all .15s;
  &:hover { border-color: #8b5cf6; background: #f5f3ff; }
  &.selected { border-color: #8b5cf6; background: #ede9fe; font-weight: 600; }
}

.open-answer { display: flex; flex-direction: column; gap: 8px; }
.photo-btn { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 8px; border: 1px dashed #8b5cf6; color: #8b5cf6; cursor: pointer; font-size: 13px; width: fit-content; }
.photo-preview { width: 80px; height: 60px; object-fit: cover; border-radius: 8px; }

.nav-row { display: flex; justify-content: space-between; align-items: center; margin-top: 24px; }
.dot-nav { display: flex; gap: 5px; }
.dot { width: 9px; height: 9px; border-radius: 50%; background: #e5e7eb; cursor: pointer; &.active { background: #8b5cf6; transform: scale(1.3); } &.answered { background: #67c23a; } }

.grading-state { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 80px; text-align: center; h3 { font-size: 20px; font-weight: 700; } .el-icon { font-size: 48px; color: #8b5cf6; } }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.result-card { background: white; border-radius: 20px; padding: 32px; box-shadow: 0 4px 24px rgba(0,0,0,.08); }
.score-display { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
.score-circle { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #8b5cf6, #6d28d9); color: white; font-size: 28px; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.score-info { h3 { font-size: 18px; font-weight: 700; margin: 0 0 4px; } p { color: var(--color-text-secondary); margin: 0; } }
.report-content { background: #f8fafc; border-radius: 12px; padding: 20px; margin-bottom: 20px; line-height: 1.8; font-size: 14px; :deep(h2) { color: #1d4ed8; margin: 12px 0 6px; } :deep(strong) { color: #1e40af; } }
</style>
