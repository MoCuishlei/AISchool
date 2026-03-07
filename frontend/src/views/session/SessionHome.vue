<template>
  <div class="session-home">
    <div class="page-header">
      <h2>🎓 我的课堂</h2>
      <p>选择继续学习或开启一门新课程</p>
    </div>

    <!-- 新建会话 -->
    <div class="new-session-card">
      <h3>📚 开启新课程</h3>
      <el-form @submit.prevent="handleCreate" class="create-form">
        <el-input v-model="newSubject" placeholder="输入学习主题，例如：Python、高中数学、机器学习..."
          size="large" clearable :disabled="isCreating">
          <template #prefix><el-icon><Reading /></el-icon></template>
        </el-input>
        <el-button type="primary" size="large" native-type="submit"
          :loading="isCreating" :disabled="!newSubject.trim()" class="create-btn">
          🚀 开始入学评测
        </el-button>
      </el-form>
      <div class="hot-subjects">
        <span class="label">热门课程：</span>
        <el-tag v-for="s in hotSubjects" :key="s" class="tag" @click="newSubject = s">{{ s }}</el-tag>
      </div>
    </div>

    <!-- 历史会话 -->
    <div v-if="sessions.length > 0" class="sessions-section">
      <h3 class="section-title">📖 继续学习</h3>
      <div class="sessions-grid">
        <div v-for="s in sessions" :key="s.session_id" class="session-card"
          @click="continueSession(s)">
          <div class="card-header">
            <span class="subject">{{ s.subject }}</span>
            <div class="header-actions">
              <el-tag :type="statusTag(s.status)" size="small">{{ statusLabel(s.status) }}</el-tag>
              <el-icon class="delete-icon" @click.stop="handleDelete(s)"><Delete /></el-icon>
            </div>
          </div>
          <div class="progress-row">
            <el-progress :percentage="s.progress_pct" :stroke-width="6"
              :color="progressColor(s.progress_pct)" />
            <span class="pct">{{ s.progress_pct }}%</span>
          </div>
          <div class="card-footer">
            <span class="time">{{ formatDate(s.updated_at) }}</span>
            <el-button type="primary" size="small" plain>继续 →</el-button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="sessions.length === 0 && !isLoading" class="empty-tip">
      <p>还没有学习记录，开启你的第一门课程吧 ✨</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStudentSessions, createSession, deleteSession } from '@/api/learning'
import { Reading, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const newSubject = ref('')
const isCreating = ref(false)
const isLoading = ref(false)
const sessions = ref<any[]>([])

const hotSubjects = ['Python 编程', '机器学习', '高中数学', '英语语法', '数据结构', '操作系统']

const statusLabel = (s: string) => ({ assessing: '测评中', learning: '学习中', finished: '已完成' }[s] || s)
const statusTag = (s: string) => ({ assessing: 'warning', learning: 'primary', finished: 'success' }[s] || 'info')
const progressColor = (p: number) => p < 30 ? '#f56c6c' : p < 70 ? '#e6a23c' : '#67c23a'
const formatDate = (d: string) => d ? new Date(d).toLocaleDateString('zh-CN') : ''

onMounted(async () => {
  isLoading.value = true
  try {
    const res: any = await getStudentSessions()
    sessions.value = res.sessions || []
  } catch { } finally { isLoading.value = false }
})

async function handleCreate() {
  if (!newSubject.value.trim()) return
  isCreating.value = true
  try {
    const res: any = await createSession(newSubject.value.trim())
    router.push(`/session/${res.session_id}/assess`)
  } catch (e: any) {
    console.error(e)
  } finally { isCreating.value = false }
}

function continueSession(s: any) {
  if (s.status === 'assessing') {
    router.push(`/session/${s.session_id}/assess`)
  } else {
    router.push(`/session/${s.session_id}/syllabus`)
  }
}

async function handleDelete(s: any) {
  try {
    await ElMessageBox.confirm(`确定要删除课程《${s.subject}》吗？所有的学习进度和对话记录将被清空，且不可恢复。`, '⚠️ 删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteSession(s.session_id)
    ElMessage.success('课程已删除')
    // 重新拉取列表
    const res: any = await getStudentSessions()
    sessions.value = res.sessions || []
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || '删除失败')
    }
  }
}
</script>

<style scoped lang="scss">
.session-home { max-width: 860px; display: flex; flex-direction: column; gap: 24px; }

.page-header {
  h2 { font-size: 22px; font-weight: 700; margin: 0 0 6px; }
  p { color: var(--color-text-secondary); margin: 0; }
}

.new-session-card {
  background: linear-gradient(135deg, #1a1f35, #2d3561);
  border-radius: 20px; padding: 28px; color: white;
  h3 { font-size: 18px; font-weight: 700; margin: 0 0 16px; }
  .create-form { display: flex; gap: 12px; margin-bottom: 14px; }
  .create-btn { flex-shrink: 0; border-radius: 10px; padding: 0 24px; background: #8b5cf6; border: none; }
  .hot-subjects { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .label { font-size: 13px; color: rgba(255,255,255,.6); }
  .tag { cursor: pointer; background: rgba(255,255,255,.1); border-color: rgba(255,255,255,.2); color: white; }
}

.section-title { font-size: 16px; font-weight: 700; margin: 0 0 14px; }

.sessions-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px;
}

.session-card {
  background: white; border-radius: 14px; padding: 18px;
  border: 2px solid var(--color-border-lighter);
  cursor: pointer; transition: all .2s;
  &:hover { border-color: #8b5cf6; box-shadow: 0 4px 16px rgba(139,92,246,.15); transform: translateY(-2px); }
}

.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.header-actions { display: flex; align-items: center; gap: 8px; }
.delete-icon {
  cursor: pointer; color: var(--color-text-secondary); font-size: 16px; padding: 4px; border-radius: 4px; transition: all .2s;
  &:hover { color: #f56c6c; background: #fef0f0; }
}
.subject { font-size: 15px; font-weight: 700; }
.progress-row { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.pct { font-size: 13px; color: var(--color-text-secondary); white-space: nowrap; }
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.time { font-size: 12px; color: var(--color-text-secondary); }

.empty-tip { text-align: center; padding: 32px; color: var(--color-text-secondary); }
</style>
