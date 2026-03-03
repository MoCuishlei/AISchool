<template>
  <div class="login-view">
    <h2 class="login-title">登录</h2>
    <el-form @submit.prevent="handleLogin" label-position="top">
      <el-form-item label="邮箱">
        <el-input v-model="email" type="email" placeholder="your@email.com" size="large" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="password" type="password" placeholder="任意密码即可" size="large" show-password />
      </el-form-item>
      <el-button
        type="primary"
        size="large"
        native-type="submit"
        style="width:100%; border-radius:10px; margin-top:8px"
        :loading="loading"
      >
        进入 AI School
      </el-button>
    </el-form>
    <p style="text-align:center; margin-top:16px; font-size:13px; color:#909399">
      演示版本，任意账号密码均可登录
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const email = ref('student@aischool.com')
const password = ref('password')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  await authStore.login(email.value, password.value)
  loading.value = false
  router.push('/dashboard')
}
</script>
