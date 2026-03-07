<template>
  <div class="dashboard">
    <!-- 顶部状态概览 -->
    <div class="stats-overview">
      <div class="overview-card main-stats">
        <div class="header-with-action">
          <div class="subject-info">
            <span class="subject-label">当前学习科目</span>
            <h2 class="subject-name">{{ analytics?.subject || '加载中...' }}</h2>
          </div>
          <div class="session-selector">
            <el-select v-model="selectedSessionId" placeholder="切换课程" size="default" style="width: 180px" @change="fetchAnalytics">
              <el-option
                v-for="s in sessions"
                :key="s.session_id"
                :label="s.subject"
                :value="s.session_id"
              />
            </el-select>
          </div>
        </div>
        <div class="progress-section">
          <div class="lp-header">
            <span>总体进度</span>
            <span>{{ analytics?.progress || 0 }}%</span>
          </div>
          <el-progress :percentage="analytics?.progress || 0" :stroke-width="12" stroke-linecap="round" color="#6366f1" />
        </div>
      </div>
      
      <div class="overview-card score-prediction">
        <div class="sp-title">预计考分预测</div>
        <div class="sp-value">{{ analytics?.projected_score || '--' }}</div>
        <div class="sp-desc">基于当前掌握情况与测验表现</div>
      </div>
    </div>

    <div v-if="loading" class="loading-state" style="padding: 100px; text-align: center;">
      <el-icon class="is-loading" :size="40" color="#6366f1"><Loading /></el-icon>
      <p style="margin-top: 16px; color: #94a3b8;">获取学情分析中...</p>
    </div>

    <div v-else-if="!analytics" class="empty-dashboard">
      <el-empty description="暂无学习数据，先开启一门课程吧">
        <router-link to="/my-courses">
          <el-button type="primary">前往课程列表</el-button>
        </router-link>
      </el-empty>
    </div>

    <!-- 图表展示区 -->
    <div v-else class="charts-container">
      <div class="chart-box trend-chart">
        <div class="cb-header">知识掌握趋势</div>
        <v-chart class="chart" :option="trendOption" autoresize />
      </div>
      
      <div class="chart-box distribution-chart">
        <div class="cb-header">领域能力分布</div>
        <v-chart class="chart" :option="radarOption" autoresize />
      </div>
    </div>

    <!-- 快捷操作入口 -->
    <div class="bottom-actions">
      <h3 class="section-title">核心学习工具</h3>
      <div class="action-grid">
        <router-link :to="`/session/${lastSessionId}/report`" class="mini-action" v-if="lastSessionId">
          <el-icon><List /></el-icon>
          <span>查看详细大纲</span>
        </router-link>
        <router-link to="/learn" class="mini-action">
          <el-icon><Lightning /></el-icon>
          <span>同步随堂讲义</span>
        </router-link>
        <router-link to="/practice" class="mini-action">
          <el-icon><EditPen /></el-icon>
          <span>强化变式练习</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getStudentSessions, api } from '@/api/learning'
import { Loading, List, Lightning, EditPen } from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, RadarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  LineChart,
  RadarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const authStore = useAuthStore()
const analytics = ref<any>(null)
const selectedSessionId = ref<number | null>(null)
const sessions = ref<any[]>([])
const loading = ref(false)

const lastSessionId = computed(() => selectedSessionId.value)

const fetchAnalytics = async () => {
  if (!selectedSessionId.value) return
  loading.value = true
  try {
    const data: any = await (api as any).get(`/analytics/dashboard/${selectedSessionId.value}`)
    analytics.value = data
  } catch (e) {
    console.error('Failed to load analytics:', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const res: any = await getStudentSessions(authStore.user?.name || '学习者')
    if (res.sessions && res.sessions.length > 0) {
      sessions.value = res.sessions
      // 默认选中第一个
      selectedSessionId.value = res.sessions[0].session_id
      await fetchAnalytics()
    }
  } catch (e) {
    console.error('Failed to load sessions:', e)
  }
})

// 趋势图配置
const trendOption = computed(() => {
  const trend = analytics.value?.trend || []
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trend.map((t: any) => t.item.substring(0, 6) + '...'),
      axisLabel: { color: '#94a3b8' }
    },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { color: '#94a3b8' } },
    series: [
      {
        name: '测验得分',
        type: 'line',
        smooth: true,
        data: trend.map((t: any) => t.score),
        itemStyle: { color: '#6366f1' },
        areaStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: 'rgba(99, 102, 241, 0.3)' }, { offset: 1, color: 'rgba(99, 102, 241, 0)' }]
          }
        }
      }
    ]
  }
})

// 雷达图配置
const radarOption = computed(() => {
  const dist = analytics.value?.mastery_distribution || {}
  const keys = Object.keys(dist).filter(k => k !== '__overall__')
  return {
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: keys.map(k => ({ name: k, max: 100 })),
      splitArea: { show: false },
      axisLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.3)' } }
    },
    series: [
      {
        name: '掌握度分析',
        type: 'radar',
        data: [{ value: keys.map(k => Math.round(dist[k])), name: '当前掌握' }],
        itemStyle: { color: '#8b5cf6' },
        areaStyle: { color: 'rgba(139, 92, 246, 0.2)' }
      }
    ]
  }
})
</script>

<style scoped lang="scss">
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stats-overview {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;

  @media (max-width: 992px) {
    grid-template-columns: 1fr;
    .score-prediction { height: 120px; }
  }
}

.overview-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid rgba(0,0,0,0.02);

  @media (max-width: 768px) {
    padding: 16px;
  }

  .theme-dark & {
    background: #1e1e2d;
    border-color: rgba(255,255,255,0.05);
  }
}

.main-stats {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 20px;

  .header-with-action {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    
    @media (max-width: 576px) {
      flex-direction: column;
      gap: 12px;
      .session-selector { width: 100% !important; .el-select { width: 100% !important; } }
    }
  }

  .subject-label { font-size: 13px; color: #64748b; margin-bottom: 4px; display: block; }
  .subject-name { font-size: 24px; font-weight: 800; color: #1e293b; margin: 0; .theme-dark & { color: white; } }
  
  .progress-section {
    .lp-header { display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; margin-bottom: 8px; color: #475569; }
  }
}

.score-prediction {
  text-align: center;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;

  .sp-title { font-size: 14px; opacity: 0.9; margin-bottom: 8px; }
  .sp-value { font-size: 48px; font-weight: 900; letter-spacing: -1px; }
  .sp-desc { font-size: 11px; opacity: 0.7; margin-top: 8px; }
}

.charts-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.chart-box {
  background: white;
  border-radius: 16px;
  padding: 24px;
  height: 360px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;

  .theme-dark & { background: #1e1e2d; }
  
  .cb-header { font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 16px; .theme-dark & { color: white; } }
  .chart { flex: 1; }
}

.bottom-actions {
  .section-title { font-size: 17px; font-weight: 700; margin-bottom: 16px; color: #1e293b; .theme-dark & { color: white; } }
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.mini-action {
  background: white;
  padding: 16px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: #475569;
  font-weight: 600;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid transparent;

  .theme-dark & { background: #1e1e2d; color: #94a3b8; }

  &:hover {
    transform: translateY(-2px);
    border-color: #6366f1;
    color: #6366f1;
    box-shadow: 0 8px 16px rgba(99, 102, 241, 0.1);
  }

  .el-icon { font-size: 20px; }
}
</style>
