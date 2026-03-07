<template>
  <div class="config-page">
    <div class="header-section">
      <h2 class="title">系统模型配置</h2>
      <p class="subtitle">在此配置 OpenAI 兼容的 LLM 接口，支持 DeepSeek, GPT, Claude 等模型对接。</p>
    </div>

    <div class="config-grid">
      <el-card class="config-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="header-title">模型接口设置</span>
            <el-tag size="small" type="primary">API 兼容 OpenAI</el-tag>
          </div>
        </template>

        <el-form :model="form" label-position="top" class="config-form">
          <el-form-item label="Base URL (接口地址)">
            <el-input 
              v-model="form.llm_base_url" 
              placeholder="例如: https://api.deepseek.com/v1" 
              clearable 
            />
          </el-form-item>
          
          <el-form-item label="API Key">
            <el-input 
              v-model="form.llm_api_key" 
              type="password" 
              show-password 
              placeholder="在此输入您的 API 密钥" 
            />
          </el-form-item>

          <el-form-item label="Model Name (模型名称)">
            <el-input 
              v-model="form.llm_model_name" 
              placeholder="例如: deepseek-chat" 
            />
          </el-form-item>

          <div class="form-actions">
            <el-button type="primary" :loading="saving" @click="saveConfigs">保存配置</el-button>
            <el-button @click="testConfig" :disabled="saving">测试连接</el-button>
          </div>
        </el-form>
      </el-card>

      <el-card class="info-card" shadow="never">
        <h3>配置说明</h3>
        <ul class="info-list">
          <li><strong>优先级</strong>: 系统将优先使用此处配置，若未设置则回退至后端环境变量配置。</li>
          <li><strong>安全性</strong>: API Key 存储在本地数据库中，建议在受信任的网络环境中使用。</li>
          <li><strong>生效范围</strong>: 包含入学测评、课堂讲解、小测验、期末考试在内的全站 AI 功能。</li>
        </ul>
        <div class="developer-link">
          <el-button type="info" plain @click="$router.push('/docs/api')">查看开发者 API 文档</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api/learning'

const form = ref({
  llm_base_url: '',
  llm_api_key: '',
  llm_model_name: ''
})

const saving = ref(false)

const fetchConfigs = async () => {
  try {
    const res: any = await (api as any).get('/config')
    const configs = res.configs || []
    configs.forEach((c: any) => {
      if (form.value.hasOwnProperty(c.key)) {
        (form.value as any)[c.key] = c.value
      }
    })
  } catch (e) {
    console.error('Failed to fetch configs', e)
  }
}

const saveConfigs = async () => {
  saving.value = true
  try {
    const keys = Object.keys(form.value) as Array<keyof typeof form.value>
    for (const key of keys) {
      await (api as any).post('/config/save', {
        key: key,
        value: form.value[key]
      })
    }
    ElMessage.success('配置保存成功，即刻生效')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const testConfig = async () => {
  try {
    const res: any = await (api as any).post('/config/test', {
      llm_base_url: form.value.llm_base_url,
      llm_api_key: form.value.llm_api_key,
      llm_model_name: form.value.llm_model_name
    })
    ElMessage.success(res.message || '连接测试成功')
  } catch (e: any) {
    ElMessage.error(e.message || '连接失败，请检查配置是否正确')
  }
}

onMounted(fetchConfigs)
</script>

<style scoped lang="scss">
.config-page {
  max-width: 1000px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 32px;
  .title { font-size: 28px; font-weight: 800; color: #1e293b; margin-bottom: 8px; }
  .subtitle { color: #64748b; font-size: 15px; }
}

.config-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 24px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.config-card {
  border-radius: 16px;
  .header-title { font-weight: 700; font-size: 17px; margin-right: 12px; }
}

.config-form {
  padding: 10px 0;
}

.form-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

.info-card {
  background: #f8fafc;
  border-radius: 16px;
  border: 1px dashed #cbd5e1;
  
  h3 { font-size: 16px; font-weight: 700; margin-bottom: 16px; }
  .info-list {
    padding-left: 20px;
    li { margin-bottom: 12px; color: #475569; font-size: 14px; line-height: 1.6; }
  }
}

.developer-link {
  margin-top: 24px;
}
</style>
