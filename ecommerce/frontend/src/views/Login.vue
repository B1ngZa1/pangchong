<template>
  <div class="min-h-screen bg-dark-950 flex items-center justify-center py-12 px-4">
    <div class="card w-full max-w-md p-8">
      <h1 class="text-2xl font-bold text-center mb-8">登录</h1>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label class="block text-sm text-dark-400 mb-2">用户名 / 邮箱</label>
          <input v-model="form.username" type="text" class="input" placeholder="请输入用户名或邮箱" required />
        </div>
        <div>
          <label class="block text-sm text-dark-400 mb-2">密码</label>
          <input v-model="form.password" type="password" class="input" placeholder="请输入密码" required />
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <p class="text-center text-dark-400 mt-6">
        还没有账号？<router-link to="/register" class="text-primary-500 hover:underline">立即注册</router-link>
      </p>

      <div class="mt-6 p-4 bg-dark-900 rounded-lg text-sm text-dark-400">
        <p class="font-medium text-dark-300 mb-2">测试账号：</p>
        <p>普通用户：testuser / test123456</p>
        <p>管理员：admin / test123456</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store'
import { useCartStore } from '@/store'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const cartStore = useCartStore()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    await userStore.login({ username: form.value.username, password: form.value.password })
    await cartStore.mergeCart()
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    error.value = e.displayMessage || e.response?.data?.detail || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
