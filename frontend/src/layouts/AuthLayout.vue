<template>
  <div class="auth-layout">
    <div class="auth-card">
      <div class="auth-header">
        <el-icon class="auth-logo"><Reading /></el-icon>
        <h1 class="auth-title">AI School</h1>
        <p class="auth-subtitle">多智能体学习辅导系统</p>
      </div>
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Reading } from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1f35 0%, #2d3561 50%, #1e3a5f 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.auth-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo {
  font-size: 48px;
  color: #3b82f6;
  margin-bottom: 12px;
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1f35;
  margin: 0 0 8px;
}

.auth-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}
</style>
