<template>
  <div v-if="show" class="settings-panel">
    <div class="settings-header">
      <span>全局设置</span>
      <el-button text @click="show = false"><el-icon><Close /></el-icon></el-button>
    </div>
    <div class="settings-body">
      <div class="setting-item">
        <span>主题</span>
        <el-radio-group v-model="themeStore.theme" @change="themeStore.setTheme($event as any)">
          <el-radio-button label="light">浅色</el-radio-button>
          <el-radio-button label="dark">深色</el-radio-button>
        </el-radio-group>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Close } from '@element-plus/icons-vue'

const themeStore = useThemeStore()
const show = ref(true)
</script>

<style scoped lang="scss">
.settings-panel {
  position: fixed;
  right: 24px;
  top: 80px;
  width: 280px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  border: 1px solid var(--color-border-light);
  z-index: 1000;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border-lighter);
  font-weight: 600;
}

.settings-body {
  padding: 16px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}
</style>
