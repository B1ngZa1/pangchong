<template>
  <div class="min-h-[75vh] bg-dark-950 flex items-center justify-center py-16 px-4">
    <div class="w-full max-w-md rounded-3xl border border-dark-800 bg-dark-900 p-6 sm:p-10 shadow-2xl">
      <p class="text-xs tracking-[0.25em] uppercase text-primary-500 mb-5">PANGCHONG · 装机计划</p>
      <h1 class="text-3xl font-bold mb-3">欢迎回来</h1>
      <p class="text-sm text-dark-400 mb-8 leading-relaxed">登录胖虫，继续完善你的配置与订单。</p>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <DsField v-model="form.username" label="用户名 / 邮箱" placeholder="请输入用户名或邮箱" autocomplete="username" required />
        <DsField v-model="form.password" label="密码" type="password" placeholder="请输入密码" autocomplete="current-password" required />

        <DsAlert v-if="error" title="登录失败" :description="error" tone="danger" role="alert" />

        <DsButton type="submit" block :loading="loading">登录</DsButton>
      </form>

      <p class="text-center text-dark-400 mt-6">
        还没有账号？<router-link :to="{ path: '/register', query: { redirect: redirectTarget } }" class="text-primary-500 hover:underline">立即注册</router-link>
      </p>

      <div v-if="isDevelopment" class="mt-6 p-4 bg-dark-950 border border-dark-800 rounded-xl text-xs text-dark-400 leading-6">
        <p class="font-medium text-dark-300 mb-2">测试账号：</p>
        <p>普通用户：testuser / test123456</p>
        <p>管理员：admin / test123456</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store'
import { useCartStore } from '@/store'
import { DsAlert, DsButton, DsField } from '@/design-system'
import { authErrorMessage, resolveAuthRedirect } from '@/utils/authNavigation'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const cartStore = useCartStore()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')
const isDevelopment = import.meta.env.DEV
const redirectTarget = computed(() => resolveAuthRedirect(route.query.redirect))

const handleLogin = async () => {
  if (loading.value) return
  loading.value = true
  error.value = ''
  try {
    await userStore.login({ username: form.value.username.trim(), password: form.value.password })
    await cartStore.mergeCart()
    await router.push(redirectTarget.value)
  } catch (e) {
    error.value = authErrorMessage(e, '登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>
